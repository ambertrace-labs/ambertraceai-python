"""The SDK's ``AmbertraceError`` carries the API's structured ``error.details``
(field + message) onto the exception and folds them into ``str(e)`` — so a
consumer catching a verified fail-closed 503 can see *which fact* was rejected
(the #209 honesty fix), instead of an opaque 503.

Robustness: a non-JSON / malformed error body must still produce a usable
exception with ``details == []`` and must not raise while being constructed.
"""

import httpx
import pytest
import respx

import ambertraceai.convenience as conv
from ambertraceai import AmbertraceAPI, AmbertraceError


@pytest.fixture(autouse=True)
def _no_sleep(monkeypatch):
    monkeypatch.setattr(conv.time, "sleep", lambda *_: None)


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url="https://test.ambertrace.ai", api_key="at_test", warm=False)
    yield client
    client.close()


# The exact body shape from the bug doc.
_REJECT_DETAIL = {
    "field": "mode3a_code",
    "message": "value '' is outside the declared domain of 'mode3a_code'",
}
_FAILCLOSED_BODY = {
    "ok": False,
    "error": {
        "code": "service_unavailable",
        "details": [_REJECT_DETAIL],
        "message": "The verified reasoning engine could not certify a result for "
                   "this query. No answer was returned.",
    },
}


class TestErrorDetailsSurfaced:
    @respx.mock
    def test_failclosed_503_carries_details(self, api):
        respx.post("https://test.ambertrace.ai/api/v1/platforms/9/query").mock(
            return_value=httpx.Response(503, json=_FAILCLOSED_BODY)
        )
        with pytest.raises(AmbertraceError) as exc:
            api.platforms.query(9, query="Triage this track.")
        e = exc.value
        # Backward-compatible attrs unchanged.
        assert e.status_code == 503
        assert e.code == "service_unavailable"
        # New: structured details exposed.
        assert e.details == [_REJECT_DETAIL]
        # str(e) names the rejected fact and the reason.
        s = str(e)
        assert "mode3a_code" in s
        assert "outside the declared domain" in s
        # API message preserved.
        assert e.message.startswith("The verified reasoning engine")
        # Optional convenience.
        assert e.rejected_facts == ["mode3a_code"]

    def test_direct_construction_matches_bug_doc(self):
        e = AmbertraceError(503, "service_unavailable",
                            "could not certify", details=[_REJECT_DETAIL])
        assert e.status_code == 503
        assert e.code == "service_unavailable"
        assert e.details == [_REJECT_DETAIL]
        assert "mode3a_code" in str(e)
        assert "outside the declared domain" in str(e)


class TestRobustFallback:
    @respx.mock
    def test_non_json_error_body_yields_empty_details(self, api):
        # A 404 with a plain-text (non-JSON) body — must not raise on construct,
        # must fall back to details == [].
        respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(404, text="Not Found")
        )
        with pytest.raises(AmbertraceError) as exc:
            api.domains.list()
        e = exc.value
        assert e.status_code == 404
        assert e.details == []
        assert e.rejected_facts == []

    @respx.mock
    def test_missing_details_key_yields_empty_list(self, api):
        respx.get("https://test.ambertrace.ai/api/v1/domains").mock(
            return_value=httpx.Response(400, json={
                "ok": False, "error": {"code": "bad_request", "message": "nope"}})
        )
        with pytest.raises(AmbertraceError) as exc:
            api.domains.list()
        assert exc.value.details == []
        assert str(exc.value) == "nope"

    @pytest.mark.parametrize("bad", [None, "oops", 42, {"field": "x"}, [1, "x", None]])
    def test_malformed_details_never_raises(self, bad):
        # Details that are not a list-of-dicts must coerce to a clean list[dict].
        e = AmbertraceError(503, "service_unavailable", "msg", details=bad)
        assert isinstance(e.details, list)
        assert all(isinstance(d, dict) for d in e.details)

    def test_error_key_not_a_dict_does_not_break(self):
        # _coerce_details handles odd shapes; constructing with no details works.
        e = AmbertraceError(500, "unknown", "boom")
        assert e.details == []
        assert str(e) == "boom"
