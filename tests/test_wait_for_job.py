"""Tests for wait_for_job polling helper."""

from unittest.mock import patch

import httpx
import pytest
import respx

from ambertraceai import AmbertraceAPI


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
    def test_returns_on_error_status(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "error", "error_message": "boom"}))
        )
        job = api.wait_for_job(1)
        assert job["status"] == "error"

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
