"""Tests for the SDK developer-experience improvements (feature-sdk-dx items 3-8):

* item 4 — consistent envelopes: ``platforms.create`` / ``build_ontology`` expose
  a normalised, stable ``id`` / ``job_id`` regardless of the underlying shape.
* item 5 — typed returns: ``datasets.upload`` / ``get`` / ``list`` return an
  ``AttrDict`` (subscript AND attribute access).
* item 6 — ``wait_for_job`` ``on_progress`` callback + ``stall_timeout``.
* item 7 — ``AmbertraceAPI.from_env`` / env-default constructor.
* item 3 — structured fail-closed query-error fields passed through to
  ``AmbertraceError`` (``missing_atoms`` / ``deciding_rule`` / ``rejected_facts`` /
  ``stalled_stage``).

All new behaviour is back-compatible: existing subscript access, the two-arg
``wait_for_job`` signature, and the explicit constructor are unchanged.
"""

from unittest.mock import patch

import httpx
import pytest
import respx

import ambertraceai.convenience as conv
from ambertraceai import AmbertraceAPI, AmbertraceError, AttrDict


def _envelope(data):
    return {"ok": True, "data": data}


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
    yield client
    client.close()


# --- AttrDict (items 4 + 5) ------------------------------------------------

class TestAttrDict:
    def test_is_a_dict(self):
        d = AttrDict({"a": 1})
        assert isinstance(d, dict)
        assert d["a"] == 1
        assert d.get("a") == 1
        assert "a" in d

    def test_attribute_access(self):
        d = AttrDict({"row_count": 100})
        assert d.row_count == 100

    def test_nested_dict_wrapped_on_access(self):
        d = AttrDict({"platform": {"id": 7}})
        assert d.platform.id == 7
        assert d["platform"]["id"] == 7

    def test_nested_list_of_dicts_wrapped(self):
        d = AttrDict({"rules": [{"id": 1}, {"id": 2}]})
        assert d.rules[0].id == 1
        assert d.rules[1].id == 2

    def test_key_shadowing_dict_method_still_subscriptable(self):
        # A key named like a dict method (e.g. "items") is reachable via
        # subscript; attribute access resolves to the method (documented limit).
        d = AttrDict({"items": [{"id": 1}]})
        assert d["items"][0]["id"] == 1
        assert callable(d.items)  # the dict method, not the value

    def test_missing_attribute_raises_attribute_error(self):
        d = AttrDict({"a": 1})
        with pytest.raises(AttributeError):
            _ = d.nope

    def test_set_and_del_attribute(self):
        d = AttrDict({})
        d.x = 5
        assert d["x"] == 5
        del d.x
        assert "x" not in d


# --- Item 4: consistent envelopes ------------------------------------------

class TestEnvelopeNormalisation:
    @respx.mock
    def test_platform_create_exposes_id_and_job_id(self, api):
        # POST /platforms returns {"platform": {...}, "build_job": {...}}.
        respx.post("https://test.ambertrace.ai/api/v1/platforms").mock(
            return_value=httpx.Response(
                200, json=_envelope({"platform": {"id": 1}, "build_job": {"id": 42}})
            )
        )
        result = api.platforms.create(domain_id=1, dataset_id=2)
        # Back-compatible original shape still works.
        assert result["platform"]["id"] == 1
        assert result["build_job"]["id"] == 42
        # New: normalised stable id / job_id (subscript AND attribute).
        assert result["id"] == 1
        assert result["job_id"] == 42
        assert result.id == 1
        assert result.job_id == 42

    @respx.mock
    def test_platform_create_handles_nested_build_job_dot_job_id(self, api):
        # An alternative shape: build_job carries a nested job.id.
        respx.post("https://test.ambertrace.ai/api/v1/platforms").mock(
            return_value=httpx.Response(
                200, json=_envelope({"platform": {"id": 3},
                                     "build_job": {"job": {"id": 99}}})
            )
        )
        result = api.platforms.create(domain_id=1, dataset_id=2)
        assert result.id == 3
        assert result.job_id == 99

    @respx.mock
    def test_platform_create_does_not_overwrite_existing_top_level_id(self, api):
        # If the API already returns a top-level id/job_id, it is preserved.
        respx.post("https://test.ambertrace.ai/api/v1/platforms").mock(
            return_value=httpx.Response(
                200, json=_envelope({"id": 5, "job_id": 7, "platform": {"id": 999}})
            )
        )
        result = api.platforms.create(domain_id=1, dataset_id=2)
        assert result.id == 5
        assert result.job_id == 7

    @respx.mock
    def test_build_ontology_exposes_job_id(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/domains/1/build-ontology").mock(
            return_value=httpx.Response(202, json=_envelope({"job_id": 11, "status": "queued"}))
        )
        result = api.domains.build_ontology(1)
        assert result.job_id == 11
        assert result["job_id"] == 11

    def test_extract_helpers_return_none_when_absent(self):
        assert conv._extract_id({"foo": 1}) is None
        assert conv._extract_job_id({"foo": 1}) is None
        assert conv._extract_id("not a dict") is None
        assert conv._extract_job_id(None) is None


# --- Item 5: typed dataset returns -----------------------------------------

class TestDatasetTypedReturns:
    @respx.mock
    def test_upload_returns_attrdict(self, api, tmp_path):
        respx.post("https://test.ambertrace.ai/api/v1/datasets/upload").mock(
            return_value=httpx.Response(201, json=_envelope(
                {"id": 5, "status": "ingested", "row_count": 200,
                 "column_count": 6, "decision_column": "outcome"}))
        )
        csv = tmp_path / "data.csv"
        csv.write_text("a,b,outcome\n1,2,approve\n")
        ds = api.datasets.upload(domain_id=1, file_path=str(csv), decision_column="outcome")
        assert isinstance(ds, AttrDict)
        # Subscript (unchanged) AND attribute access (new — discoverable fields).
        assert ds["id"] == 5
        assert ds.row_count == 200
        assert ds.column_count == 6
        assert ds.decision_column == "outcome"

    @respx.mock
    def test_get_returns_attrdict(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/datasets/5").mock(
            return_value=httpx.Response(200, json=_envelope(
                {"id": 5, "name": "ds", "row_count": 10}))
        )
        ds = api.datasets.get(5)
        assert isinstance(ds, AttrDict)
        assert ds.row_count == 10

    @respx.mock
    def test_list_items_are_attrdicts(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/datasets").mock(
            return_value=httpx.Response(200, json=_envelope(
                [{"id": 1, "row_count": 3}, {"id": 2, "row_count": 4}]))
        )
        items = api.datasets.list()
        assert all(isinstance(d, AttrDict) for d in items)
        assert items[0].row_count == 3
        assert items[1].id == 2


# --- Item 6: wait_for_job progress + stall ---------------------------------

class TestWaitForJobProgress:
    @respx.mock
    def test_on_progress_called_each_poll(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 1, "status": "building_ontology", "progress": 0})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "building", "progress": 50})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "ready", "progress": 100})),
            ]
        )
        seen = []
        with patch("time.sleep"):
            job = api.wait_for_job(1, on_progress=lambda j: seen.append(j.get("progress")))
        assert job["status"] == "ready"
        # Callback fired on every poll including the terminal one.
        assert seen == [0, 50, 100]

    @respx.mock
    def test_stall_timeout_raises_on_no_forward_progress(self, api):
        # Job is stuck at building_ontology progress 0 forever.
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope(
                {"id": 1, "status": "building_ontology", "progress": 0}))
        )
        # monotonic: deadline calc (0), init last_progress_at (0), then each
        # loop pass reads time twice (now, and the marker-equal branch). Provide
        # a steadily-advancing clock so the stall fires before the overall timeout.
        times = iter([0, 0, 0, 0, 5, 5, 31, 31, 31])
        with patch("time.sleep"), patch("time.monotonic", lambda: next(times)):
            with pytest.raises(TimeoutError, match="stalled"):
                api.wait_for_job(1, timeout=600, stall_timeout=30)

    @respx.mock
    def test_stall_timeout_not_tripped_when_progressing(self, api):
        # Progress advances each poll → stall clock keeps resetting → completes.
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            side_effect=[
                httpx.Response(200, json=_envelope({"id": 1, "status": "building", "progress": 10})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "building", "progress": 60})),
                httpx.Response(200, json=_envelope({"id": 1, "status": "ready", "progress": 100})),
            ]
        )
        with patch("time.sleep"):
            job = api.wait_for_job(1, stall_timeout=30)
        assert job["status"] == "ready"

    @respx.mock
    def test_back_compatible_two_arg_signature(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/jobs/1").mock(
            return_value=httpx.Response(200, json=_envelope({"id": 1, "status": "ready"}))
        )
        job = api.wait_for_job(1, timeout=300, poll_interval=5)
        assert job["status"] == "ready"


# --- Item 7: from_env / env-default constructor ----------------------------

class TestFromEnv:
    def test_from_env_reads_key_and_base_url(self, monkeypatch):
        monkeypatch.setenv("AMBERTRACE_API_KEY", "at_envkey")
        monkeypatch.setenv("AMBERTRACE_BASE_URL", "https://custom.example.com")
        api = AmbertraceAPI.from_env(warm=False)
        assert str(api._http.base_url) == "https://custom.example.com"
        assert api._http.headers["authorization"] == "Bearer at_envkey"
        api.close()

    def test_from_env_defaults_base_url(self, monkeypatch):
        monkeypatch.setenv("AMBERTRACE_API_KEY", "at_envkey")
        monkeypatch.delenv("AMBERTRACE_BASE_URL", raising=False)
        api = AmbertraceAPI.from_env(warm=False)
        assert str(api._http.base_url) == "https://app.ambertrace.ai"
        api.close()

    def test_from_env_raises_without_key(self, monkeypatch):
        monkeypatch.delenv("AMBERTRACE_API_KEY", raising=False)
        with pytest.raises(ValueError, match="No API key"):
            AmbertraceAPI.from_env(warm=False)

    def test_from_env_loads_dotenv(self, monkeypatch, tmp_path):
        monkeypatch.delenv("AMBERTRACE_API_KEY", raising=False)
        monkeypatch.delenv("AMBERTRACE_BASE_URL", raising=False)
        env = tmp_path / ".env"
        env.write_text(
            "# comment\n"
            "export AMBERTRACE_API_KEY='at_fromfile'\n"
            'AMBERTRACE_BASE_URL="https://file.example.com"\n'
        )
        api = AmbertraceAPI.from_env(dotenv_path=str(env), warm=False)
        assert api._http.headers["authorization"] == "Bearer at_fromfile"
        assert str(api._http.base_url) == "https://file.example.com"
        api.close()

    def test_real_env_wins_over_dotenv(self, monkeypatch, tmp_path):
        monkeypatch.setenv("AMBERTRACE_API_KEY", "at_real")
        monkeypatch.delenv("AMBERTRACE_BASE_URL", raising=False)
        env = tmp_path / ".env"
        env.write_text("AMBERTRACE_API_KEY=at_file\n")
        api = AmbertraceAPI.from_env(dotenv_path=str(env), warm=False)
        assert api._http.headers["authorization"] == "Bearer at_real"
        api.close()

    def test_constructor_env_fallback(self, monkeypatch):
        # No explicit args → constructor reads env (item 7).
        monkeypatch.setenv("AMBERTRACE_API_KEY", "at_ctorenv")
        monkeypatch.delenv("AMBERTRACE_BASE_URL", raising=False)
        api = AmbertraceAPI(warm=False)
        assert api._http.headers["authorization"] == "Bearer at_ctorenv"
        assert str(api._http.base_url) == "https://app.ambertrace.ai"
        api.close()

    def test_explicit_arg_wins_over_env(self, monkeypatch):
        monkeypatch.setenv("AMBERTRACE_API_KEY", "at_env")
        api = AmbertraceAPI(api_key="at_explicit", base_url="https://example.com", warm=False)
        assert api._http.headers["authorization"] == "Bearer at_explicit"
        api.close()

    def test_load_dotenv_missing_file_returns_empty(self):
        assert conv._load_dotenv("/no/such/file.env") == {}


# --- Item 3: structured fail-closed query error fields ---------------------

class TestStructuredQueryError:
    @respx.mock
    def test_query_error_passes_through_structured_fields(self, api):
        # Fields nested under error.* (parity with authorize_action).
        body = {
            "ok": False,
            "error": {
                "code": "service_unavailable",
                "message": "the policy chain did not reach the decision layer",
                "missing_atoms": ["is_eligible", "risk_band"],
                "deciding_rule": "permit_when_eligible",
                "rejected_facts": ["applicant_age"],
                "stalled_stage": "decision",
            },
        }
        respx.post("https://test.ambertrace.ai/api/v1/platforms/9/query").mock(
            return_value=httpx.Response(503, json=body)
        )
        with pytest.raises(AmbertraceError) as exc:
            api.platforms.query(9, query="Assess this applicant.")
        e = exc.value
        assert e.missing_atoms == ["is_eligible", "risk_band"]
        assert e.deciding_rule == "permit_when_eligible"
        assert e.rejected_facts == ["applicant_age"]
        assert e.stalled_stage == "decision"

    @respx.mock
    def test_query_error_fields_at_top_level(self, api):
        # Robust to the fields landing at the top level of the body instead.
        body = {
            "ok": False,
            "error": {"code": "service_unavailable", "message": "no decision"},
            "missing_atoms": ["foo"],
            "stalled_stage": "classify",
        }
        respx.post("https://test.ambertrace.ai/api/v1/platforms/9/query").mock(
            return_value=httpx.Response(503, json=body)
        )
        with pytest.raises(AmbertraceError) as exc:
            api.platforms.query(9, query="q")
        assert exc.value.missing_atoms == ["foo"]
        assert exc.value.stalled_stage == "classify"

    @respx.mock
    def test_absent_fields_default_empty_back_compatible(self, api):
        # Older deployment that omits the structured fields entirely.
        respx.get("https://test.ambertrace.ai/api/v1/domains/9").mock(
            return_value=httpx.Response(404, json={
                "ok": False, "error": {"code": "not_found", "message": "nope"}})
        )
        with pytest.raises(AmbertraceError) as exc:
            api.domains.get(9)
        e = exc.value
        assert e.missing_atoms == []
        assert e.deciding_rule is None
        assert e.rejected_facts == []
        assert e.stalled_stage is None

    def test_rejected_facts_falls_back_to_details_when_no_explicit_list(self):
        # No explicit rejected_facts → fall back to detail field names.
        e = AmbertraceError(503, "x", "msg", details=[{"field": "f1", "message": "m"}])
        assert e.rejected_facts == ["f1"]

    def test_explicit_rejected_facts_preferred_over_details(self):
        e = AmbertraceError(503, "x", "msg",
                            details=[{"field": "f1", "message": "m"}],
                            rejected_facts=["explicit"])
        assert e.rejected_facts == ["explicit"]
