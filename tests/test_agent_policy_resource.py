"""Offline contract tests for the Agent Policy Gate SDK surface.

Asserts the new ``api.agent_policy`` convenience methods hit the correct routes
with the correct request bodies and parse the response envelope — using a mocked
transport (respx), so they run with no live API. The real-path proof that the
compiled obligations FIRE on the gate lives in
``tests/api/test_sdk_agent_policy_e2e.py`` (real kernel + real checker).
"""

import httpx
import pytest
import respx

from ambertraceai import AgentPolicyResource, AmbertraceAPI, AmbertraceError

BASE = "https://test.ambertrace.ai"


def _env(data):
    return {"ok": True, "data": data}


@pytest.fixture
def api():
    client = AmbertraceAPI(base_url=BASE, api_key="at_test", warm=False)
    yield client
    client.close()


def test_agent_policy_property_returns_resource(api):
    assert isinstance(api.agent_policy, AgentPolicyResource)


@respx.mock
def test_author_posts_policy_text(api):
    route = respx.post(f"{BASE}/api/v1/agent-policy-gate/policy").mock(
        return_value=httpx.Response(200, json=_env({
            "platform": {"id": 7, "verified_profile": True},
            "admitted": [{"name": "exposure_within_limit", "kind": "derive",
                          "description": "cumulative exposure within the limit"}],
            "rejected": [],
            "policy_text": "cumulative exposure must stay within 100000",
        })),
    )
    import json
    result = api.agent_policy.author("cumulative exposure must stay within 100000")
    assert route.called
    assert json.loads(route.calls.last.request.read()) == \
        {"policy_text": "cumulative exposure must stay within 100000"}
    assert result["platform"]["id"] == 7
    assert result["admitted"][0]["name"] == "exposure_within_limit"


@respx.mock
def test_status_gets_gate(api):
    respx.get(f"{BASE}/api/v1/agent-policy-gate").mock(
        return_value=httpx.Response(200, json=_env({
            "enabled": True, "platform": {"id": 7},
            "admitted_controls": [{"name": "exposure_within_limit",
                                   "description": "..."}],
            "input_fields": [{"name": "qty", "type": "int"},
                             {"name": "price", "type": "float"}],
        })),
    )
    status = api.agent_policy.status()
    assert {f["name"] for f in status["input_fields"]} == {"qty", "price"}


@respx.mock
def test_examples_gets_library(api):
    respx.get(f"{BASE}/api/v1/example-policies").mock(
        return_value=httpx.Response(200, json=_env([
            {"id": "energy-grid-dispatch", "title": "Grid dispatch controller",
             "policy_text": "...", "try_hint": "..."},
        ])),
    )
    examples = api.agent_policy.examples()
    assert examples[0]["id"] == "energy-grid-dispatch"


@respx.mock
def test_authorize_action_posts_action_and_context(api):
    route = respx.post(f"{BASE}/api/v1/platforms/7/authorize-action").mock(
        return_value=httpx.Response(200, json=_env({
            "decision": "permit", "proof_checked": True, "proof_summary": "...",
            "denied_reason": None, "certified_facts": [], "rejected_facts": [],
        })),
    )
    verdict = api.agent_policy.authorize_action(
        7, tool="place_order", args={"qty": 100, "price": 400},
        context={"day": "mon"})
    assert route.called
    import json
    sent = json.loads(route.calls.last.request.read())
    assert sent == {"action": {"tool": "place_order",
                               "args": {"qty": 100, "price": 400}},
                    "context": {"day": "mon"}}
    assert verdict["decision"] == "permit"
    assert verdict["proof_checked"] is True


@respx.mock
def test_authorize_action_omits_context_when_none(api):
    route = respx.post(f"{BASE}/api/v1/platforms/7/authorize-action").mock(
        return_value=httpx.Response(200, json=_env({"decision": "deny"})),
    )
    api.agent_policy.authorize_action(7, tool="t", args={"a": 1})
    import json
    sent = json.loads(route.calls.last.request.read())
    assert "context" not in sent
    assert sent["action"] == {"tool": "t", "args": {"a": 1}}


@respx.mock
def test_session_lifecycle(api):
    respx.post(f"{BASE}/api/v1/agent-sessions").mock(
        return_value=httpx.Response(201, json=_env({"id": "sid1", "trace": []})),
    )
    respx.post(f"{BASE}/api/v1/agent-sessions/sid1/step").mock(
        return_value=httpx.Response(200, json=_env({
            "session": {"id": "sid1"},
            "step": {"verdict": {"decision": "permit", "proof_checked": True},
                     "executed": True},
        })),
    )
    respx.get(f"{BASE}/api/v1/agent-sessions/sid1").mock(
        return_value=httpx.Response(200, json=_env({"id": "sid1", "trace": [{}]})),
    )

    session = api.agent_policy.create_session(platform_id=7, goal="place orders")
    assert session["id"] == "sid1"
    step = api.agent_policy.step("sid1", tool="place_order",
                                 args={"qty": 1, "price": 1})
    assert step["step"]["executed"] is True
    trace = api.agent_policy.get_session("sid1")
    assert trace["id"] == "sid1"


@respx.mock
def test_author_404_when_gate_disabled(api):
    respx.post(f"{BASE}/api/v1/agent-policy-gate/policy").mock(
        return_value=httpx.Response(404, json={"error": {"code": "not_found",
                                                          "message": "Not found."}}),
    )
    with pytest.raises(AmbertraceError) as exc:
        api.agent_policy.author("anything")
    assert exc.value.status_code == 404
