"""27 — Agent Policy Gate (single-action, English-authored, proof-carrying).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
You write the policy an agent must obey in a few sentences; Ambertrace compiles it
to a verified policy and PROVES every proposed tool-call permit/deny against it —
fail-closed, with a machine-checked proof. The LLM only *proposes*; the kernel
*proves*.

The scenario: a clinical-triage assistant agent. The policy (a real preset from
``api.agent_policy.examples()``, the "healthcare-triage" one) admits a few
PER-ACTION obligations:

  - Only allow actions of type triage, schedule, or refer.
  - Do not approve an opioid refill unless prior_authorization is present.
  - Escalate any message that mentions self-harm.

This demo gates TWO single proposed actions through ``authorize_action``:

  1. A compliant action (a referral with prior authorization present) → expect
     PERMIT, with a certified proof.
  2. A non-compliant action (an opioid refill with NO prior authorization) →
     expect DENY, fail-closed, with the failing requirement named.

For each it prints the verdict's PROOF CERTIFICATE: decision, permitted,
proof_checked, deciding_rule, certified_facts, rejected_facts, denied_reason.

IP boundary: the proof certificate is an OUTPUT the verified engine produces — it
demonstrates the RESULT (which facts were certified, which rule decided, that the
firing set was machine-checked). It does NOT ship or reveal the kernel / Lean
formalisation that produces it; you read the certificate, the engine stays
internal.

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The Agent Policy Gate is a
preview capability (feature-flagged server-side); when it is not enabled on your
deployment its endpoints return 404, which this demo reports cleanly and skips.
For the CUMULATIVE-obligation flow (a running budget proven over a mediated
session), see ``25_agent_spend_budget.py``.

Creates resources on your account. Run with --help for options.

    python 27_agent_policy_gate.py
    python 27_agent_policy_gate.py -v
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The example-policy id we author (one of api.agent_policy.examples()). Falls back
# to an inline copy of the same policy text if the deployment's library differs.
POLICY_ID = "healthcare-triage"

POLICY_TEXT_FALLBACK = (
    "Escalate to a clinician any message that mentions self-harm. "
    "Do not approve an opioid refill unless prior_authorization is present. "
    "Only allow actions of type triage, schedule, or refer."
)

# Two single proposed actions to gate. ``args`` are the action's intrinsic fields;
# ``context`` carries ambient facts the policy reasons over. We supply a value for
# every declared input the gate reports, so it returns a real permit/deny rather
# than rejecting an unknown/missing fact. (label, tool, args, context, expected)
ACTIONS = [
    (
        "A compliant referral — action_type=refer, prior_authorization present",
        "refer",
        {"action_type": "refer", "prior_authorization": True},
        {"message": "Routine follow-up; please refer to cardiology."},
        "permit",
    ),
    (
        "An opioid refill with NO prior authorization (policy forbids)",
        "approve_refill",
        {"action_type": "schedule", "is_opioid_refill": True,
         "prior_authorization": False},
        {"message": "Requesting an early opioid refill."},
        "deny",
    ),
]


def _resolve_policy_text(api) -> str:
    """The healthcare-triage preset's policy_text from the live example library,
    or the inline fallback if the library is unavailable / shaped differently."""
    try:
        examples = api.agent_policy.examples() or []
    except AmbertraceError:
        return POLICY_TEXT_FALLBACK
    for ex in examples:
        if ex.get("id") == POLICY_ID and ex.get("policy_text"):
            return ex["policy_text"]
    return POLICY_TEXT_FALLBACK


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _print_inputs(status: dict) -> None:
    inputs = status.get("input_fields") or []
    if not inputs:
        print("  No declared input fields: the gate constrains whatever the action "
              "proposes.")
        return
    print(f"  Declared input fields an action should supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        enum = spec.get("enum_values")
        enum_s = f" one of {enum}" if enum else ""
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}{enum_s}")


def _print_certificate(verdict: dict, expected: str) -> None:
    """Print the verdict's PROOF CERTIFICATE — the engine's OUTPUT.

    These fields demonstrate the RESULT; they do not reveal the kernel/Lean
    formalisation that produced them.
    """
    decision = verdict.get("decision")
    mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
    print(f"    decision:       {str(decision).upper()}  {mark}")
    print(f"    permitted:      {verdict.get('permitted')}")
    print(f"    proof_checked:  {verdict.get('proof_checked')}")
    if verdict.get("deciding_rule"):
        print(f"    deciding_rule:  {verdict.get('deciding_rule')}")
    certified = verdict.get("certified_facts") or []
    rejected = verdict.get("rejected_facts") or []
    if certified:
        print(f"    certified_facts ({len(certified)}): {certified}")
    if rejected:
        print(f"    rejected_facts  ({len(rejected)}): {rejected}")
    if verdict.get("denied_reason"):
        print(f"    denied_reason:  {verdict.get('denied_reason')}")
    if verdict.get("proof_summary"):
        print(f"    proof_summary:  {verdict.get('proof_summary')}")


def run_agent_policy_gate_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring a per-action policy (English in)")
    policy_text = _resolve_policy_text(api)
    print(f"  POLICY:\n    {policy_text}\n")

    try:
        result = api.agent_policy.author(policy_text)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) — skipping.")
            return
        raise

    platform = result.get("platform") or {}
    platform_id = platform.get("id")
    print(f"  Authored verified policy -> platform {platform_id} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)

    print_section(2, 3, "Reviewing the declared input fields")
    _print_inputs(api.agent_policy.status())

    print_section(3, 3, "Gating single proposed actions (permit + deny, WITH PROOF)")
    for label, tool, action_args, context, expected in ACTIONS:
        print(f"\n  {'-' * 66}\n  {label}")
        verdict = api.agent_policy.authorize_action(
            platform_id, tool=tool, args=action_args, context=context)
        _print_certificate(verdict, expected)

    print("\nDone. Each verdict above is proof-carrying: a permit means the kernel "
          "certified the action satisfies every policy requirement; a deny means it "
          "could NOT, fail-closed, naming the requirement that failed. The proof "
          "certificate is the engine's OUTPUT — it shows the result, not the "
          "kernel/Lean formalisation that produced it.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Policy Gate — AmberTrace AI verified per-action "
                    "governance for AI-agent actions (English-authored, "
                    "proof-carrying permit/deny)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_agent_policy_gate_demo, args)


if __name__ == "__main__":
    main()
