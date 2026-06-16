"""37 — Agent PII-Egress Gate (per-action condition, English-authored).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
You write the data-egress rule in a sentence; Ambertrace compiles it to a
verified policy and PROVES every proposed outbound message permit/deny against
the message's OWN fields — fail-closed, with a machine-checked proof.

The scenario: an autonomous agent may send outbound messages, but any message
whose payload carries a social security number or a credit card number must be
blocked. Each decision depends only on the proposed message itself — no history
is needed — so we gate ONE action at a time with ``authorize_action`` (no
session). This is a per-action CONDITION over the action's declared PII flags.

What it shows:

  1. Author the PII-egress policy in ENGLISH (per-action-condition obligation)
  2. Read back the admitted rules (plain English) + the declared input fields
  3. Gate a small set of proposed messages one at a time:
       - a clean message (no SSN, no credit card) -> PERMIT + proof
       - a message that contains a social security number -> DENY + proof
       - a message that contains a credit card number -> DENY + proof
       - a message that contains only an email address -> PERMIT + proof

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The Agent Policy Gate is a
preview capability; when it is not enabled on your deployment the endpoints
return 404, which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 37_agent_pii_egress_gate.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# A per-action-condition policy, authored in plain English. The compiler admits
# verified obligations checked against the proposed message's OWN fields: the
# payload must contain neither a social security number nor a credit card number.
PII_EGRESS_POLICY = (
    "An autonomous agent may send outbound messages. Any message whose payload "
    "contains a social security number or a credit card number must be blocked. "
    "Permit a send only when the payload contains neither a social security "
    "number nor a credit card number."
)

# A small set of proposed messages, gated one at a time (no session — each
# decision depends only on the message's own PII flags).
#   (label, tool, args, expected)
ACTION_LIST = [
    ("clean message — no SSN, no credit card", "send_message",
     {"contains_ssn": False, "contains_credit_card": False}, "permit"),
    ("message contains a social security number", "send_message",
     {"contains_ssn": True, "contains_credit_card": False}, "deny"),
    ("message contains a credit card number", "send_message",
     {"contains_ssn": False, "contains_credit_card": True}, "deny"),
    ("message contains only an email address", "send_message",
     {"contains_ssn": False, "contains_credit_card": False,
      "contains_email": True}, "permit"),
]


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
        # No declared inputs at all (e.g. a policy with no per-action operands).
        print("  No declared input fields: the gate still constrains whatever the "
              "action proposes.")
        return
    # A per-action-condition policy reads its operands directly from the proposed
    # action; those operand fields are surfaced as input_fields, so an action
    # supplies them as args and the gate proves the obligation against them.
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        enum = ""
        if spec.get("enum_values"):
            enum = f" {{{', '.join(str(v) for v in spec['enum_values'])}}}"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}{enum}")


def _gate_action(api, platform_id: int, label: str, tool: str,
                 args: dict, expected: str) -> None:
    print(f"\n  {'-' * 66}\n  {label}")
    verdict = api.agent_policy.authorize_action(platform_id, tool=tool, args=args)
    decision = verdict.get("decision")
    mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
    print(f"    Decision:      {str(decision).upper()}  {mark}")
    print(f"    proof_checked: {verdict.get('proof_checked')}")
    if decision != "permit" and verdict.get("denied_reason"):
        print(f"    denied_reason: {verdict.get('denied_reason')}")


def _author_and_gate(api, policy_text: str, actions, title: str) -> bool:
    """Author a policy and gate each proposed action through it.

    Returns False (and reports cleanly) if the gate is not enabled (404)."""
    try:
        result = api.agent_policy.author(policy_text)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("\n  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) — skipping.")
            return False
        raise
    platform = result.get("platform") or {}
    print(f"  Authored verified policy -> platform {platform.get('id')} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)

    status = api.agent_policy.status()
    _print_inputs(status)

    print_section(3, 3, f"Gating proposed messages one at a time ({title})")
    for label, tool, args, expected in actions:
        _gate_action(api, platform["id"], label, tool, args, expected)
    return True


def run_pii_egress_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the PII-egress policy (English in)")
    print(f"  POLICY:\n    {PII_EGRESS_POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    enabled = _author_and_gate(api, PII_EGRESS_POLICY, ACTION_LIST, "per-action condition")
    if not enabled:
        return

    print("\nDone. Every decision above is proof-carrying: a permit means the "
          "kernel certified the payload carries neither a social security number "
          "nor a credit card number; a deny means it could NOT, fail-closed, and "
          "the send is blocked.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent PII-Egress Gate — AmberTrace AI verified per-action-"
                    "condition governance for AI-agent actions (English-authored)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_pii_egress_demo, args)


if __name__ == "__main__":
    main()
