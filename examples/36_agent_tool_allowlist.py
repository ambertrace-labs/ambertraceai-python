"""36 — Agent Tool-Allowlist Gate (per-action condition, English-authored).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
This is the SIMPLEST, introductory gate: you write the allowlist rule in a
sentence; Ambertrace compiles it to a verified policy and PROVES every proposed
action permit/deny against the action's OWN fields — fail-closed, with a
machine-checked proof.

The scenario: an autonomous operations agent may only run a fixed set of action
types (read / search / summarize), and any action whose operating pressure is
outside a safe band must be blocked. Each decision depends only on the proposed
action itself — no history is needed — so we gate ONE action at a time with
``authorize_action`` (no session). This is a per-action CONDITION, the most basic
obligation class.

What it shows:

  1. Author the allowlist policy in ENGLISH (per-action-condition obligation)
  2. Read back the admitted rules (plain English) + the declared input fields
  3. Gate a small set of proposed actions one at a time:
       - an allowed action type within the safe band -> PERMIT + proof
       - an action type that is not on the allowlist -> DENY + proof
       - an allowed type with an in-band pressure -> PERMIT + proof
       - an out-of-band pressure -> DENY + proof

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The Agent Policy Gate is a
preview capability; when it is not enabled on your deployment the endpoints
return 404, which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 36_agent_tool_allowlist.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The allowed action types and the safe operating-pressure band.
ALLOWED_TYPES = ("read", "search", "summarize")
PRESSURE_LO, PRESSURE_HI = 2, 8

# A per-action-condition policy, authored in plain English. The compiler admits
# verified obligations checked against the proposed action's OWN fields: the
# action type must be on the allowlist, and pressure_bar must be in [2, 8].
ALLOWLIST_POLICY = (
    "An autonomous operations agent may only execute actions of type read, "
    "search, or summarize. Any action whose pressure_bar value is outside the "
    f"range {PRESSURE_LO} to {PRESSURE_HI} must be blocked. Permit an action "
    "only when it satisfies both conditions."
)

# A small set of proposed actions, gated one at a time (no session — each
# decision depends only on the action's own fields).
#   (label, tool, args, expected)
ACTION_LIST = [
    ("read within band (pressure 5)", "read",
     {"type": "read", "pressure_bar": 5}, "permit"),
    ("write — not on the allowlist", "write",
     {"type": "write", "pressure_bar": 5}, "deny"),
    ("summarize within band (pressure 5)", "summarize",
     {"type": "summarize", "pressure_bar": 5}, "permit"),
    ("command, pressure 12 — OUT OF BAND", "command",
     {"type": "command", "pressure_bar": 12}, "deny"),
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

    print_section(3, 3, f"Gating proposed actions one at a time ({title})")
    for label, tool, args, expected in actions:
        _gate_action(api, platform["id"], label, tool, args, expected)
    return True


def run_tool_allowlist_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the tool-allowlist policy (English in)")
    print(f"  POLICY:\n    {ALLOWLIST_POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    enabled = _author_and_gate(api, ALLOWLIST_POLICY, ACTION_LIST, "per-action condition")
    if not enabled:
        return

    print("\nDone. Every decision above is proof-carrying: a permit means the "
          "kernel certified the action is an allowed type within the safe band; "
          "a deny means it could NOT, fail-closed, and the action is blocked.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Tool-Allowlist Gate — AmberTrace AI verified per-action-"
                    "condition governance for AI-agent actions (English-authored)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_tool_allowlist_demo, args)


if __name__ == "__main__":
    main()
