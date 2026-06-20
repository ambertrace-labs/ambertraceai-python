"""Tests for SDK resource methods — mocked HTTP."""

from unittest.mock import patch

import httpx
import pytest
import respx

from ambertraceai import AmbertraceAPI, AmbertraceError


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
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

    @respx.mock
    def test_upload_sends_decision_column(self, api, tmp_path):
        route = respx.post("https://test.ambertrace.ai/api/v1/datasets/upload").mock(
            return_value=httpx.Response(201, json=_envelope({"id": 5, "status": "ingested"}))
        )
        csv = tmp_path / "data.csv"
        csv.write_text("a,b,decision\n1,2,approve\n")
        result = api.datasets.upload(
            domain_id=1, file_path=str(csv), decision_column="decision")
        assert route.called
        assert result["id"] == 5
        # Multipart form must carry the decision_column field.
        body = route.calls.last.request.content.decode("utf-8", "ignore")
        assert "decision_column" in body
        assert "decision" in body

    @respx.mock
    def test_fetch_multi_posts_sources(self, api):
        route = respx.post("https://test.ambertrace.ai/api/v1/datasets/fetch-multi").mock(
            return_value=httpx.Response(202, json=_envelope({"id": 9, "status": "processing"}))
        )
        sources = [
            {"connector_type": "fred", "config": {"series_ids": ["GS10"]}},
            {"connector_type": "boe", "config": {"series_ids": ["IUDSOIA"]}},
        ]
        result = api.datasets.fetch_multi(
            domain_id=1, sources=sources, frequency="monthly", aggregation="last")
        assert route.called
        assert result["id"] == 9
        sent = route.calls.last.request
        import json as _json
        payload = _json.loads(sent.content)
        assert payload["domain_id"] == 1
        assert payload["join_on"] == "date"
        assert payload["frequency"] == "monthly"
        assert payload["aggregation"] == "last"
        assert len(payload["sources"]) == 2


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

    @respx.mock
    def test_discover_no_wait_returns_envelope(self, api):
        route = respx.post(
            "https://test.ambertrace.ai/api/v1/platforms/1/discover-prediction-rules"
        ).mock(
            return_value=httpx.Response(
                202,
                json=_envelope({"job_id": 7, "status": "discovering", "poll": "/api/v1/jobs/7"}),
            )
        )
        result = api.predictions.discover_prediction_rules(
            1, prediction_config_id=5, max_rounds=2, wait=False,
        )
        assert route.called
        # max_rounds is forwarded in the POST body.
        sent = route.calls.last.request
        assert b'"max_rounds":2' in sent.content
        assert b'"prediction_config_id":5' in sent.content
        assert result["job_id"] == 7

    @respx.mock
    def test_discover_wait_polls_job_to_result(self, api):
        respx.post(
            "https://test.ambertrace.ai/api/v1/platforms/1/discover-prediction-rules"
        ).mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 9, "status": "discovering"}))
        )
        respx.get("https://test.ambertrace.ai/api/v1/jobs/9").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 9, "status": "processing"})),
                httpx.Response(
                    200,
                    json=_envelope({
                        "id": 9, "status": "completed",
                        "result": {"prediction_config_id": 5, "total_accepted": 2,
                                   "total_rejected": 3, "rounds": 1, "converged": True,
                                   "convergence_reason": "no_accept"},
                    }),
                ),
            ]
        )
        with patch("time.sleep"):
            result = api.predictions.discover_prediction_rules(1, prediction_config_id=5)
        assert result["total_accepted"] == 2
        assert result["converged"] is True

    @respx.mock
    def test_discover_wait_raises_on_failed_job(self, api):
        respx.post(
            "https://test.ambertrace.ai/api/v1/platforms/1/discover-prediction-rules"
        ).mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 11, "status": "discovering"}))
        )
        respx.get("https://test.ambertrace.ai/api/v1/jobs/11").mock(
            return_value=httpx.Response(
                200, json=_envelope({"id": 11, "status": "failed", "error_message": "boom"})
            )
        )
        with pytest.raises(AmbertraceError) as exc_info:
            api.predictions.discover_prediction_rules(1, prediction_config_id=5)
        assert exc_info.value.code == "job_failed"

    @respx.mock
    def test_discovered_prediction_rules(self, api):
        route = respx.get(
            "https://test.ambertrace.ai/api/v1/platforms/1/discovered-prediction-rules"
        ).mock(
            return_value=httpx.Response(
                200,
                json=_envelope({
                    "platform_id": 1, "prediction_config_id": 5, "total_accepted": 1,
                    "accepted_rules": [{"id": 3, "name": "r", "fire_rate": 0.4, "delta": -0.02}],
                }),
            )
        )
        result = api.predictions.discovered_prediction_rules(1, prediction_config_id=5)
        assert route.called
        assert "prediction_config_id=5" in str(route.calls.last.request.url)
        assert result["accepted_rules"][0]["fire_rate"] == 0.4

    @respx.mock
    def test_neurosymbolic_comparison_wait_polls(self, api):
        respx.get(
            "https://test.ambertrace.ai/api/v1/platforms/1/neurosymbolic-comparison"
        ).mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 21, "status": "comparing"}))
        )
        respx.get("https://test.ambertrace.ai/api/v1/jobs/21").mock(
            return_value=httpx.Response(
                200,
                json=_envelope({
                    "id": 21, "status": "completed",
                    "result": {"platform_id": 1, "prediction_config_id": 5, "target": "GS10",
                               "neural": {"r2": 0.8, "rmse": 0.3, "mae": 0.2, "n": 24},
                               "neurosymbolic": {"r2": 0.85, "rmse": 0.27, "mae": 0.18, "n": 24},
                               "delta": {"r2": 0.05, "rmse": -0.03},
                               "n_adjustment_rules": 1, "n_constraint_rules": 0, "fire_rate": 0.4},
                }),
            )
        )
        with patch("time.sleep"):
            result = api.predictions.neurosymbolic_comparison(1, prediction_config_id=5)
        assert result["delta"]["r2"] == 0.05
        assert result["neural"]["r2"] == 0.8

    @respx.mock
    def test_neurosymbolic_comparison_no_wait_returns_envelope(self, api):
        respx.get(
            "https://test.ambertrace.ai/api/v1/platforms/1/neurosymbolic-comparison"
        ).mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 21, "status": "comparing"}))
        )
        result = api.predictions.neurosymbolic_comparison(1, prediction_config_id=5, wait=False)
        assert result["job_id"] == 21

    @respx.mock
    def test_neurosymbolic_comparison_include_series(self, api):
        route = respx.get(
            "https://test.ambertrace.ai/api/v1/platforms/1/neurosymbolic-comparison"
        ).mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 21, "status": "comparing"}))
        )
        respx.get("https://test.ambertrace.ai/api/v1/jobs/21").mock(
            return_value=httpx.Response(
                200,
                json=_envelope({
                    "id": 21, "status": "completed",
                    "result": {"platform_id": 1, "prediction_config_id": 5, "target": "GS10",
                               "neural": {"r2": 0.8, "rmse": 0.3, "mae": 0.2, "n": 2},
                               "neurosymbolic": {"r2": 0.85, "rmse": 0.27, "mae": 0.18, "n": 2},
                               "delta": {"r2": 0.05, "rmse": -0.03},
                               "n_adjustment_rules": 1, "n_constraint_rules": 0, "fire_rate": 0.5,
                               "series": [
                                   {"index": 0, "time": "2024-01-01", "actual": 4.0,
                                    "neural": 4.1, "neurosymbolic": 4.05, "rule_fired": True},
                                   {"index": 1, "actual": 4.2,
                                    "neural": 4.2, "neurosymbolic": 4.2, "rule_fired": False},
                               ]},
                }),
            )
        )
        with patch("time.sleep"):
            result = api.predictions.neurosymbolic_comparison(
                1, prediction_config_id=5, include_series=True)
        # include_series is wired into the query params
        assert "include_series=true" in str(route.calls.last.request.url).lower()
        assert len(result["series"]) == 2
        assert result["series"][0]["rule_fired"] is True
        assert result["series"][1]["rule_fired"] is False
