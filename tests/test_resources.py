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
    def test_create_returns_platform_and_build_job(self, api):
        # POST /platforms returns {"platform": {...}, "build_job": {...}}
        respx.post("https://test.ambertrace.ai/api/v1/platforms").mock(
            return_value=httpx.Response(
                200, json=_envelope({"platform": {"id": 1}, "build_job": {"id": 42}})
            )
        )
        result = api.platforms.create(domain_id=1, dataset_id=2)
        assert result["platform"]["id"] == 1
        assert result["build_job"]["id"] == 42

    @respx.mock
    def test_query_returns_answer(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms/1/query").mock(
            return_value=httpx.Response(200, json=_envelope({"answer": "yes", "explanation": "because"}))
        )
        result = api.platforms.query(1, query="test?")
        assert result["answer"] == "yes"
        assert result["explanation"] == "because"


class TestConnectorResource:
    @respx.mock
    def test_list_returns_connectors(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/connectors").mock(
            return_value=httpx.Response(200, json=_envelope([{"type": "fred"}]))
        )
        result = api.connectors.list()
        assert result[0]["type"] == "fred"

    @respx.mock
    def test_test_sends_type_and_config(self, api):
        route = respx.post("https://test.ambertrace.ai/api/v1/connectors/test").mock(
            return_value=httpx.Response(200, json=_envelope({"rows": 3, "columns": ["a"], "sample": []}))
        )
        result = api.connectors.test(connector_type="fred", config={"series_id": "GDP"})
        assert route.called
        assert result["rows"] == 3


class TestPredictionResource:
    @respx.mock
    def test_predict_returns_result(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms/1/predict").mock(
            return_value=httpx.Response(200, json=_envelope({"predicted_value": 42.0, "confidence": 0.9}))
        )
        result = api.predictions.predict(1, prediction_config_id=1, feature_overrides={"x": 1})
        assert result["predicted_value"] == 42.0
        assert result["confidence"] == 0.9


class TestPlatformRulesCRUD:
    @respx.mock
    def test_list_rules(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/platforms/1/rules").mock(
            return_value=httpx.Response(200, json=_envelope([{"id": 1, "name": "r1"}]))
        )
        result = api.platforms.list_rules(1)
        assert len(result) == 1

    @respx.mock
    def test_create_rule(self, api):
        route = respx.post("https://test.ambertrace.ai/api/v1/platforms/1/rules").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 10, "name": "test_rule"}))
        )
        result = api.platforms.create_rule(
            1, name="test_rule",
            condition={"field": "x", "operator": "==", "value": 1},
            action={"type": "derive", "value": "y"},
        )
        assert result["id"] == 10
        assert route.called

    @respx.mock
    def test_update_rule(self, api):
        route = respx.patch("https://test.ambertrace.ai/api/v1/platforms/1/rules/10").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 10, "description": "updated"}))
        )
        api.platforms.update_rule(1, 10, description="updated")
        assert route.called

    @respx.mock
    def test_delete_rule(self, api):
        route = respx.delete("https://test.ambertrace.ai/api/v1/platforms/1/rules/10").mock(
            return_value=httpx.Response(200, json=_envelope({"deleted": True}))
        )
        api.platforms.delete_rule(1, 10)
        assert route.called


class TestPlatformDrift:
    @respx.mock
    def test_capture_drift_baseline(self, api):
        route = respx.post("https://test.ambertrace.ai/api/v1/platforms/1/drift/baseline").mock(
            return_value=httpx.Response(200, json=_envelope({"platform_id": 1, "certified_rejection_rate": 0.02}))
        )
        result = api.platforms.capture_drift_baseline(1)
        assert result["certified_rejection_rate"] == 0.02
        assert route.called

    @respx.mock
    def test_check_drift(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/platforms/1/drift/check").mock(
            return_value=httpx.Response(200, json=_envelope({"platform_id": 1, "drift_detected": False, "alerts": []}))
        )
        result = api.platforms.check_drift(1)
        assert result["drift_detected"] is False

    @respx.mock
    def test_update_verified_settings(self, api):
        route = respx.patch("https://test.ambertrace.ai/api/v1/platforms/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "verified_profile": True}))
        )
        api.platforms.update(1, verified_min_confidence=0.9)
        assert route.called
