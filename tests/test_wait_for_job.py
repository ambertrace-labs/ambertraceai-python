"""Tests for wait_for_job polling helper."""

from unittest.mock import patch

import httpx
import pytest
import respx

from ambertraceai import AmbertraceAPI, AmbertraceError


def _envelope(data):
    return {"ok": True, "data": data}


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
    yield client
    client.close()


class TestWaitForJob:
    @respx.mock
    def test_returns_on_ready_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 1, "status": "processing"})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "ready"})),
            ]
        )
        with patch("time.sleep"):
            job = api.wait_for_job(1)
        assert job["status"] == "ready"

    @respx.mock
    def test_returns_on_active_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "active"}))
        )
        job = api.wait_for_job(1)
        assert job["status"] == "active"

    @respx.mock
    def test_returns_on_completed_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "completed"}))
        )
        job = api.wait_for_job(1)
        assert job["status"] == "completed"

    @respx.mock
    def test_raises_on_error_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "error", "error_message": "boom"}))
        )
        with pytest.raises(AmbertraceError, match="boom") as exc:
            api.wait_for_job(1)
        assert exc.value.code == "job_failed"

    @respx.mock
    def test_raises_on_failed_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "failed", "error_message": "ontology gen exploded"}))
        )
        with pytest.raises(AmbertraceError, match="ontology gen exploded"):
            api.wait_for_job(1)

    @respx.mock
    def test_raises_on_failed_status_without_error_message(self, api):
        # No error_message — message falls back to the status.
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "failed"}))
        )
        with pytest.raises(AmbertraceError, match="failed"):
            api.wait_for_job(1)

    @respx.mock
    def test_needs_review_is_not_a_failure(self, api):
        # A build that completes with build_quality warnings is status=ready —
        # NOT a failure — so it must still return the job dict.
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({
                "id": 1, "status": "ready",
                "result": {"build_quality": {"status": "needs_review"}},
            }))
        )
        job = api.wait_for_job(1)
        assert job["status"] == "ready"
        assert job["result"]["build_quality"]["status"] == "needs_review"

    @respx.mock
    def test_raises_on_timeout(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "processing"}))
        )
        with patch("time.sleep"), patch("time.monotonic", side_effect=[0, 0, 301]):
            with pytest.raises(TimeoutError, match="did not complete"):
                api.wait_for_job(1, timeout=300)

    @respx.mock
    def test_respects_poll_interval(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 1, "status": "processing"})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "ready"})),
            ]
        )
        with patch("time.sleep") as mock_sleep:
            api.wait_for_job(1, poll_interval=10)
        mock_sleep.assert_called_with(10)

    @respx.mock
    def test_default_timeout_600s(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "processing"}))
        )
        with patch("time.sleep"), patch("time.monotonic", side_effect=[0, 0, 601]):
            with pytest.raises(TimeoutError):
                api.wait_for_job(1)

    @respx.mock
    def test_default_poll_interval_5s(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 1, "status": "processing"})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "ready"})),
            ]
        )
        with patch("time.sleep") as mock_sleep:
            api.wait_for_job(1)
        mock_sleep.assert_called_with(5)
