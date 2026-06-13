"""25 — Agent Spend-Budget Gate (cumulative exposure, English-authored).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
You write the budget rule in a sentence; Ambertrace compiles it to a verified
policy and PROVES every proposed action permit/deny against the CUMULATIVE spend
so far — fail-closed, with a machine-checked proof, and the gate is the sole
executor (no effect without a prior certified permit).

The scenario: an autonomous procurement agent may place orders, but its TOTAL
committed spend across the session must stay within a budget. Each order's
exposure is ``quantity x unit_price``; the policy caps the running sum of
``quantity x unit_price`` over the order ledger. Individually every order is
fine — the control is the CUMULATIVE total, which a per-action check cannot
express. This is the obligation the verified gate adds.

What it shows:

  1. Author the budget policy in ENGLISH (cumulative-exposure obligation)
  2. Read back the admitted rules (plain English) + the declared input fields
  3. Open a mediated session and step a synthetic, seeded order stream:
       - orders that keep the running spend within budget -> PERMIT + proof,
         executed (the row joins the ledger)
       - the order that would push cumulative spend over budget -> DENY + proof,
         NOT executed (the obligation fact is absent from the proof)
  4. (optional) author a BAND variant: an order whose fill price is only known to
     lie in an interval [lo, hi] — the bound is proven for EVERY price in the band

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The order stream is
synthetic and seeded (reproducible). The Agent Policy Gate is a preview
capability; when it is not enabled on your deployment the endpoints return 404,
which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 25_agent_spend_budget.py
    python 25_agent_spend_budget.py --band   # also run the interval-band variant
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The budget. Cumulative spend = sum of (quantity x unit_price) over the ledger.
BUDGET = 100_000

# A cumulative-exposure policy, authored in plain English. The compiler admits a
# verified EXPOSURE obligation: sum of quantity x unit_price over the order ledger
# must stay within BUDGET.
SPEND_POLICY = (
    "An autonomous procurement agent may place purchase orders. Each order is "
    "recorded as a row in a purchase_orders ledger with a quantity column and a "
    "unit_price column. The cumulative spend — the sum of quantity times "
    "unit_price across every row in the purchase_orders ledger — must stay at or "
    f"below {BUDGET}. Permit a purchase order only when the resulting cumulative "
    "spend stays within that budget."
)

# A BAND variant (--band): the proposed order's fill price is not yet known but is
# guaranteed to fall in [lo, hi]; the bound must hold for EVERY price in the band.
PRICE_LO, PRICE_HI = 200, 400
SPEND_POLICY_BAND = (
    "An autonomous procurement agent may place purchase orders against a "
    "purchase_orders ledger that has a quantity column and a unit_price column. "
    f"For a proposed order whose fill price is not yet known but is guaranteed to "
    f"be between {PRICE_LO} and {PRICE_HI}, the cumulative spend — the sum of "
    f"quantity times unit_price across all rows — must stay at or below {BUDGET} "
    "for every possible fill price in that range. Permit the order only when that "
    "bound holds for all prices in the band."
)

# A synthetic, seeded order stream. Running spend after each: 40k, 80k, 120k.
# The third order is individually fine (40k) but pushes the cumulative total over
# the 100k budget — that is the one the verified gate must DENY.
#   (label, quantity, unit_price, expected)
ORDER_STREAM = [
    ("order 1: 100 units @ 400  (running 40,000)", 100, 400, "permit"),
    ("order 2: 100 units @ 400  (running 80,000)", 100, 400, "permit"),
    ("order 3: 100 units @ 400  (running 120,000 — OVER BUDGET)", 100, 400, "deny"),
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
        # A pure cumulative-exposure policy reads its quantity/price from the
        # LEDGER ROW each action contributes, not from scalar facts — so there are
        # no scalar input_fields. The action supplies the row (here: quantity +
        # unit_price, the purchase_orders ledger's columns).
        print("  No scalar input fields: this is a cumulative (ledger) policy — "
              "each action supplies a row to the purchase_orders ledger "
              "(quantity + unit_price), and the gate proves the obligation over "
              "the resulting ledger.")
        return
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}")


def _run_stream(api, platform_id: int, stream) -> None:
    session = api.agent_policy.create_session(
        platform_id=platform_id, goal="place purchase orders within budget")
    sid = session["id"]
    print(f"  Mediated session {sid} opened (the gate is the sole executor).")

    for label, qty, price, expected in stream:
        print(f"\n  {'-' * 66}\n  {label}")
        step = api.agent_policy.step(
            sid, tool="place_order",
            args={"quantity": qty, "unit_price": price})
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


def run_spend_budget_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the spend-budget policy (English in)")
    print(f"  POLICY:\n    {SPEND_POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    enabled = _author_and_run(api, SPEND_POLICY, ORDER_STREAM, "cumulative exposure")
    if not enabled:
        return

    if args.band:
        print(f"\n{'=' * 70}\nBAND VARIANT — the bound is proven for EVERY price "
              f"in [{PRICE_LO}, {PRICE_HI}]\n{'=' * 70}")
        print(f"  POLICY:\n    {SPEND_POLICY_BAND}\n")
        # The band obligation is verified for ALL prices in the declared interval
        # (a universal bound), not for a single sampled price — so a live order
        # stream would not add to what the read-back already shows. We author it
        # and read back the admitted interval-band obligation, the discoverable
        # proof that English -> a verified band control compiles.
        try:
            result = api.agent_policy.author(SPEND_POLICY_BAND)
        except AmbertraceError as exc:
            if getattr(exc, "status_code", None) == 404:
                print("\n  The Agent Policy Gate is not enabled — skipping band variant.")
                return
            raise
        platform = result.get("platform") or {}
        print(f"  Authored verified band policy -> platform {platform.get('id')} "
              f"({platform.get('status')}, verified={platform.get('verified_profile')})")
        _print_admitted(result)
        print("\n  The band obligation above proves the cumulative spend stays "
              f"within budget for EVERY fill price in [{PRICE_LO}, {PRICE_HI}] — a "
              "universal bound, not a sampled check.")

    print("\nDone. Every decision above is proof-carrying: a permit means the "
          "kernel certified the cumulative spend stays within budget; a deny "
          "means it could NOT, fail-closed, and the order never executed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Spend-Budget Gate — AmberTrace AI verified cumulative-"
                    "exposure governance for AI-agent actions (English-authored)",
    )
    add_common_args(parser)
    parser.add_argument(
        "--band", action="store_true",
        help="Also run the interval-band variant (bound proven for all prices in "
             "a declared [lo, hi] band).",
    )
    args = parser.parse_args()
    run_demo(run_spend_budget_demo, args)


if __name__ == "__main__":
    main()
