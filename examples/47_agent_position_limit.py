"""47 — Agent Position-Limit Gate (cumulative sum, English-authored).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
You write the position cap in a sentence; Ambertrace compiles it to a verified
policy and PROVES every proposed order permit/deny against the CUMULATIVE
position so far — fail-closed, with a machine-checked proof, and the gate is the
sole executor (no effect without a prior certified permit).

The scenario: an autonomous trading agent may place buy orders, but its TOTAL
position across the session must stay within a cap. The running position is the
SUM of the order quantity over the positions ledger; the policy caps that
running sum of ``quantity`` over the ledger. Individually every order is fine —
the control is the CUMULATIVE position, which a per-action check cannot express.
This is the obligation the verified gate adds.

What it shows:

  1. Author the position-limit policy in ENGLISH (cumulative-sum obligation)
  2. Read back the admitted rules (plain English) + the declared input fields
  3. Open a mediated session and step a synthetic, seeded order stream:
       - orders that keep the running position within the cap -> PERMIT + proof,
         executed (the row joins the ledger)
       - the order that would push cumulative position over the cap -> DENY +
         proof, NOT executed (the obligation fact is absent from the proof)

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The order stream is
synthetic and seeded (reproducible). The Agent Policy Gate is a preview
capability; when it is not enabled on your deployment the endpoints return 404,
which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 47_agent_position_limit.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The cap. Cumulative position = sum of quantity over the positions ledger.
MAX_POSITION = 1000

# A cumulative-sum policy, authored in plain English. The compiler admits a
# verified SUM obligation: sum of quantity over the positions ledger must stay
# within MAX_POSITION.
POLICY = (
    "An autonomous trading agent may place buy orders for an instrument. Each "
    "order is recorded as a row in a positions ledger with a quantity column. "
    "The cumulative position — the sum of quantity across every row in the "
    f"positions ledger — must stay at or below {MAX_POSITION} lots. Permit an "
    "order only when the resulting cumulative position stays within that limit."
)

# A synthetic, seeded order stream. Running position after each: 400, 800, 1200.
# The third order is individually fine (400) but pushes the cumulative position
# over the 1000-lot cap — that is the one the verified gate must DENY.
#   (label, quantity, expected)
ORDER_STREAM = [
    ("buy 400 lots (running 400)", 400, "permit"),
    ("buy 400 lots (running 800)", 400, "permit"),
    ("buy 400 lots (running 1200 — OVER LIMIT)", 400, "deny"),
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
    # A cumulative-sum policy reads its operand (quantity) from the LEDGER ROW
    # each action contributes; that operand column is surfaced as an input_field,
    # so an action supplies it as an arg and the gate proves the obligation over
    # the resulting ledger.
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}")


def _run_stream(api, platform_id: int, stream) -> None:
    session = api.agent_policy.create_session(
        platform_id=platform_id, goal="place buy orders within the position limit")
    sid = session["id"]
    print(f"  Mediated session {sid} opened (the gate is the sole executor).")

    for label, qty, expected in stream:
        print(f"\n  {'-' * 66}\n  {label}")
        step = api.agent_policy.step(
            sid, tool="place_order",
            args={"quantity": qty})
        verdict = (step.get("step") or {}).get("verdict") or {}
        executed = (step.get("step") or {}).get("executed")
        decision = verdict.get("decision")
        mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
        print(f"    Decision:      {str(decision).upper()}  {mark}")
        print(f"    proof_checked: {verdict.get('proof_checked')}")
        print(f"    executed:      {executed}")
        if decision != "permit" and verdict.get("denied_reason"):
            print(f"    denied_reason: {verdict.get('denied_reason')}")

    # The trace proves the mediation invariant: only the permitted orders ran.
    trace = api.agent_policy.get_session(sid).get("trace") or []
    executed = [t for t in trace if t.get("executed")]
    print(f"\n  Executed {len(executed)} of {len(trace)} proposed orders "
          "(an effect occurs only after a certified permit).")


def _author_and_run(api, policy_text: str, stream, title: str) -> bool:
    """Author a policy and run the order stream through the gate.

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

    print_section(3, 3, f"Stepping the synthetic order stream ({title})")
    _run_stream(api, platform["id"], stream)
    return True


def run_position_limit_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the position-limit policy (English in)")
    print(f"  POLICY:\n    {POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    _author_and_run(api, POLICY, ORDER_STREAM, "cumulative sum")

    print("\nDone. Every decision above is proof-carrying: a permit means the "
          "kernel certified the cumulative position stays within the cap; a deny "
          "means it could NOT, fail-closed, and the order never executed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Position-Limit Gate — AmberTrace AI verified cumulative-"
                    "sum governance for AI-agent actions (English-authored)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_position_limit_demo, args)


if __name__ == "__main__":
    main()
