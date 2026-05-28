"""Tests for SDK resource methods — mocked HTTP."""

import httpx
import pytest
import respx

from ambertraceai import AmbertraceAPI, AmbertraceError


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test")
    yield client
    client.close()


def _envelope(data):
    return {"ok": True, "data": data}


def _error(code, message, status=400):
    return {"ok": False, "error": {"code": code, "message": message}}


class TestDomainResource:
    @respx.mock
    def test_create_sends_post(self, api):
        route = respx.post("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "name": "Test"}))
        )
        result = api.domains.create(name="Test", description="A test domain")
        assert route.called
        assert result["id"] == 1

    @respx.mock
    def test_list_returns_list(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(200, json=_envelope([{"id": 1}, {"id": 2}]))
        )
        result = api.domains.list()
        assert len(result) == 2

    @respx.mock
    def test_get_returns_domain(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/domains/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "name": "Test"}))
        )
        result = api.domains.get(1)
        assert result["name"] == "Test"

    @respx.mock
    def test_delete_sends_delete(self, api):
        route = respx.delete("https://test.ambertrace.ai/api/v1/domains/1").mock(
            return_value=httpx.Response(200, json=_envelope({"deleted": True}))
        )
        api.domains.delete(1)
        assert route.called

    @respx.mock
    def test_not_found_raises_error(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/domains/999").mock(
            return_value=httpx.Response(404, json=_error("not_found", "Domain not found."))
        )
        with pytest.raises(AmbertraceError) as exc_info:
            api.domains.get(999)
        assert exc_info.value.status_code == 404
        assert exc_info.value.code == "not_found"


class TestDatasetResource:
    @respx.mock
    def test_quality_returns_report(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/datasets/1/quality").mock(
            return_value=httpx.Response(200, json=_envelope({"score": 0.85}))
        )
        result = api.datasets.quality(1)
        assert result["score"] == 0.85

    @respx.mock
    def test_list_returns_datasets(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/datasets").mock(
            return_value=httpx.Response(200, json=_envelope([{"id": 1}]))
        )
        result = api.datasets.list()
        assert len(result) == 1


class TestPlatformResource:
    @respx.mock
    def test_create_returns_job_reference(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms").mock(
            return_value=httpx.Response(200, json=_envelope({"platform_id": 1, "job_id": 42}))
        )
        result = api.platforms.create(domain_id=1, dataset_id=2)
        assert result["job_id"] == 42

    @respx.mock
    def test_query_returns_answer(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms/1/query").mock(
            return_value=httpx.Response(200, json=_envelope({"answer": "yes", "explanation": "because"}))
        )
        result = api.platforms.query(1, query="test?")
        assert result["answer"] == "yes"
        assert result["explanation"] == "because"


class TestPredictionResource:
    @respx.mock
    def test_predict_returns_result(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms/1/predict").mock(
            return_value=httpx.Response(200, json=_envelope({"predicted_value": 42.0, "confidence": 0.9}))
        )
        result = api.predictions.predict(1, input_data={"x": 1})
        assert result["predicted_value"] == 42.0
        assert result["confidence"] == 0.9
