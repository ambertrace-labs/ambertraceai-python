"""40 — Agent Policy Gate: TEMPORAL precedence (review-before-deploy, proof-carrying).

A NATIVE happens-before obligation, authored in PLAIN ENGLISH. Unlike a boolean
precondition the caller asserts (example 28's ``code_review_approved``), this gate
proves the real BEFORE/AFTER ORDERING of the events themselves over the session's
certified ORDERED ledger of executed actions. The policy:

    "Permit a production deploy for a service only when it is preceded by an
     approval for the same service in the same session. Block any deploy that has
     not been preceded by an approval for that service."

compiles to a verified PRECEDENCE obligation (the ``precededBy`` temporal leaf):
every deploy on a service must be preceded, in order, by an approval on the SAME
service. The kernel folds this over the accumulated ordered ledger and proves it.

WHY A SESSION (not a single authorize_action). A temporal obligation reads the
ORDER of prior EXECUTED actions, so it needs the accumulated ledger — a
``create_session`` + ``step`` loop. A single ``authorize_action`` gates an EMPTY
ledger, so the first deploy has nothing to be preceded by and is denied. The
harness is the sole executor: an action's row joins the ledger only after the gate
PERMITS it (so the approval must itself permit to become a preceding event).

THE ORDER-SENSITIVITY PAYOFF. The same multiset of events in a DIFFERENT order
yields a DIFFERENT verdict — that is exactly what a boolean precondition cannot do:

  * approve(checkout) then deploy(checkout)   -> PERMIT  (deploy is preceded)
  * deploy(checkout) with no prior approval   -> DENY    (un-preceded, fail-closed)
  * deploy(checkout) BEFORE its approval      -> DENY    (both events occur, but the
                                                          deploy was not yet preceded;
                                                          a late approval does NOT
                                                          retroactively authorise it)
  * approve(payments) then deploy(checkout)   -> DENY    (approval was for a
                                                          DIFFERENT service)

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. Authoring REPLACES the org's
single agent-policy gate (see 25/27/28). The Agent Policy Gate is a preview
capability (feature-flagged server-side); when it is not enabled — or your
credentials lack write authority over an existing org gate — ``author`` returns 404,
which this demo reports cleanly and skips. Temporal obligations additionally require
the platform's verified temporal fragment to be enabled on the deployment.

    python 40_agent_policy_gate_temporal.py
    python 40_agent_policy_gate_temporal.py -v
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The approval-before-deploy ordering policy, authored in plain English. The
# compiler admits a verified PRECEDENCE obligation over the ordered session ledger.
POLICY = (
    "A deployment agent proposes approve and deploy actions, each for a named "
    "service. An approval may be recorded for a service. Permit a deploy for a "
    "service only when it is preceded by an approval for the same service in the "
    "same session. Block any deploy that has not been preceded by an approval for "
    "that service."
)

# Each scenario is one MEDIATED SESSION: a sequence of proposed actions and the
# expected verdict for each step. The order is the whole point.
#   (scenario_title, [ (label, tool, args, expected_decision), ... ])
SCENARIOS = [
    ("compliant order — approve THEN deploy the same service", [
        ("approve(checkout)", "approve", {"action": "approve", "service": "checkout"}, "permit"),
        ("deploy(checkout)  — preceded by its approval", "deploy",
         {"action": "deploy", "service": "checkout"}, "permit"),
    ]),
    ("un-preceded deploy — no approval at all", [
        ("deploy(checkout)  — nothing precedes it", "deploy",
         {"action": "deploy", "service": "checkout"}, "deny"),
    ]),
    ("WRONG ORDER — deploy BEFORE its approval (order-sensitivity payoff)", [
        ("deploy(checkout)  — issued before any approval", "deploy",
         {"action": "deploy", "service": "checkout"}, "deny"),
        ("approve(checkout) — arrives too late to authorise the earlier deploy", "approve",
         {"action": "approve", "service": "checkout"}, "permit"),
    ]),
    ("WRONG SERVICE — approval is for a different service", [
        ("approve(payments)", "approve", {"action": "approve", "service": "payments"}, "permit"),
        ("deploy(checkout)  — its own service was never approved", "deploy",
         {"action": "deploy", "service": "checkout"}, "deny"),
    ]),
]


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s) (the authoritative read-back):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _run_scenario(api, platform_id: int, title: str, steps) -> None:
    session = api.agent_policy.create_session(
        platform_id=platform_id, goal="mediate ordered deploys")
    sid = session["id"]
    print(f"\n  {'-' * 68}\n  SESSION {sid}: {title}")
    for label, tool, args, expected in steps:
        step = api.agent_policy.step(sid, tool=tool, args=args)
        verdict = (step.get("step") or {}).get("verdict") or {}
        executed = (step.get("step") or {}).get("executed")
        decision = verdict.get("decision")
        mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
        print(f"    {label}")
        print(f"      decision: {str(decision).upper():7s} {mark}   "
              f"proof_checked={verdict.get('proof_checked')}  executed={executed}")
        if decision != "permit" and verdict.get("denied_reason"):
            print(f"      denied_reason: {verdict.get('denied_reason')}")
    # Only permitted actions joined the ledger — the mediation invariant.
    trace = api.agent_policy.get_session(sid).get("trace") or []
    executed_n = len([t for t in trace if t.get("executed")])
    print(f"      -> {executed_n} of {len(trace)} proposed action(s) executed "
          "(an effect occurs only after a certified permit).")


def run_temporal_gate_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the approval-before-deploy ordering policy (English in)")
    print(f"  POLICY:\n    {POLICY}\n")

    try:
        result = api.agent_policy.author(POLICY)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability), or your credentials lack write authority "
                  "over an existing org gate — skipping.")
            return
        raise

    platform = result.get("platform") or {}
    platform_id = platform.get("id")
    print(f"  Authored verified policy -> platform {platform_id} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)

    print_section(2, 3, "The declared input contract")
    status = api.agent_policy.status()
    inputs = status.get("input_fields") or []
    if inputs:
        print(f"  Supply each on every action ({len(inputs)}):")
        for spec in inputs:
            print(f"    - {spec.get('name')} ({spec.get('type')})")
    else:
        print("  (the gate constrains whatever the action proposes)")

    print_section(3, 3, "Stepping ordered sessions — the ORDER decides the verdict")
    for title, steps in SCENARIOS:
        _run_scenario(api, platform_id, title, steps)

    print("\nDone. Every verdict is proof-carrying and ORDER-sensitive: a deploy "
          "permits only when the ordered ledger proves an approval for the same "
          "service came BEFORE it — a native happens-before obligation, not a "
          "caller-asserted boolean.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Policy Gate — verified TEMPORAL precedence "
                    "(review-before-deploy) governance for AI-agent actions")
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_temporal_gate_demo, args)


if __name__ == "__main__":
    main()
