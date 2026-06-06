"""Cold-start resilience: the SDK rides over the scale-to-zero wake window
(retry on infra-unavailability + proactive warm-up + keep-alive) WITHOUT
masking a real app response (a verified-profile fail-closed 503 surfaces
immediately).
"""

import httpx
import pytest
import respx

import ambertraceai.convenience as conv
from ambertraceai import AmbertraceAPI, AmbertraceError


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    # Don't actually sleep through backoff in tests.
    monkeypatch.setattr(conv.time, "sleep", lambda *_: None)


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
    yield client
    client.close()


def _env(data):
    return {"ok": True, "data": data}


class TestRetryOnInfraUnavailable:
    @respx.mock
    def test_retries_non_json_503_then_succeeds(self, api):
        # Fly proxy 503 (no JSON envelope) twice, then the woken app responds.
        route = respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            side_effect=[
                httpx.Response(503, text="no healthy instances"),
                httpx.Response(503, text="no healthy instances"),
                httpx.Response(200, json=_env([{"id": 1}])),
            ]
        )
        result = api.domains.list()
        assert result == [{"id": 1}]
        assert route.call_count == 3

    @respx.mock
    def test_retries_transport_error_then_succeeds(self, api):
        route = respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            side_effect=[
                httpx.ConnectError("connection refused"),
                httpx.Response(200, json=_env([{"id": 2}])),
            ]
        )
        assert api.domains.list() == [{"id": 2}]
        assert route.call_count == 2

    @respx.mock
    def test_gives_up_after_max_retries(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(503, text="still waking")
        )
        with pytest.raises(AmbertraceError) as exc:
            api.domains.list()
        assert exc.value.status_code == 503
        assert exc.value.code == "backend_unavailable"


class TestDoesNotMaskRealResponses:
    @respx.mock
    def test_verified_failclosed_503_surfaces_immediately(self, api):
        # A 503 WITH the app envelope is a deliberate verified-profile
        # fail-closed — it must NOT be retried, and must surface as-is.
        route = respx.post("https://test.ambertrace.ai/api/v1/platforms/9/query").mock(
            return_value=httpx.Response(503, json={
                "ok": False,
                "error": {"code": "certification_failed",
                          "message": "could not certify a result"}})
        )
        with pytest.raises(AmbertraceError) as exc:
            api.platforms.query(9, query="q")
        assert exc.value.status_code == 503
        assert exc.value.code == "certification_failed"
        assert route.call_count == 1   # NOT retried

    @respx.mock
    def test_app_400_not_retried(self, api):
        route = respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(404, json={
                "ok": False, "error": {"code": "not_found", "message": "nope"}})
        )
        with pytest.raises(AmbertraceError) as exc:
            api.domains.list()
        assert exc.value.code == "not_found"
        assert route.call_count == 1


class TestWarmAndKeepAlive:
    @respx.mock
    def test_warm_on_init_pings_health(self):
        route = respx.get("https://test.ambertrace.ai/ambertrace/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=True)
        client.close()
        assert route.called

    @respx.mock
    def test_warm_false_does_not_ping(self):
        route = respx.get("https://test.ambertrace.ai/ambertrace/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
        client.close()
        assert not route.called

    @respx.mock
    def test_warm_init_failure_is_swallowed(self):
        respx.get("https://test.ambertrace.ai/ambertrace/health").mock(
            side_effect=httpx.ConnectError("down")
        )
        # Must not raise — warm-up is best-effort.
        client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=True)
        client.close()

    @respx.mock
    def test_wait_for_job_pings_health_between_polls(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/5").mock(
            side_effect=[
                httpx.Response(200, json=_env({"id": 5, "status": "processing"})),
                httpx.Response(200, json=_env({"id": 5, "status": "ready"})),
            ]
        )
        health = respx.get("https://test.ambertrace.ai/ambertrace/health").mock(
            return_value=httpx.Response(200, json={"status": "ok"})
        )
        job = api.wait_for_job(5, timeout=30, poll_interval=0)
        assert job["status"] == "ready"
        assert health.called   # kept warm during the poll loop
