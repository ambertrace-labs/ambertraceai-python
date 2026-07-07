"""39 — Federal gift-acceptance ethics gate (5 CFR 2635 Subpart B).

Can a government AI obey the law? This encodes the Standards of Ethical Conduct for
Employees of the Executive Branch, 5 CFR Part 2635 Subpart B (Gifts From Outside
Sources), as a verified decision domain and decides real gift-acceptance scenarios
with a machine-checked proof each.

The codifiable core — the prohibited-source test, the $20-per-source-per-occasion and
$50-annual thresholds, the cash-equivalent and bribery overrides — becomes a
classify-then-conclude gate. The open-textured layer (the reasonable-person appearance
test, whether a gift is really from personal friendship) is NOT forced into logic: when
a case turns on judgment, the gate **escalates** to a human ethics official rather than
auto-permitting. A department's ethics code is exactly this shape — a hard skeleton plus
a few judgment joints; the gate governs the skeleton and hands the joints to a human.

Design notes (what makes it build + resolve cleanly):
  * classify-then-conclude with POSITIVE intermediate atoms; precedence is carried by the
    first-matching-rule order (bribe-decline beats the $20 exception; escalate beats
    permit), not by negation inside atoms;
  * ``decline`` is the fail-closed default (a verified gate should refuse, not guess);
  * per-source / per-occasion / annual dollar aggregates are supplied as facts — the
    caller sums the items (a mechanical step); the gate applies the legal thresholds and
    overrides.

Scenarios and their ground-truth verdicts are the CFR's own worked examples. Illustrative
encoding for demonstration — not legal advice, not affiliated with or endorsed by any
agency.

LIVE RESULTS
------------
14 / 14 CFR worked examples decide as the regulation requires; every verdict comes back
``proof_checked=True``. Highlights:
  * bribery override BEATS the $20 exception — a $15 gift card conditioned on an official
    action DECLINES (the hard rule fires before the small-gift exception);
  * a cash-equivalent (financial-institution gift card) DECLINES even under $20, while an
    identical-value RETAIL gift card PERMITS;
  * $20 / $50 aggregation — $18 + $15 = $33 from one source on one occasion DECLINES, but
    the $18 subset alone PERMITS; four $10 gifts ($40 annual) PERMIT while a fifth taking
    the annual total to $60 DECLINES;
  * the appearance-judgment case (a sub-$20 lunch right after a promotional pitch)
    ESCALATES to a human rather than auto-permitting — the honest boundary is the pitch.

    python 39_federal_ethics_gift_gate.py             # build + decide the CFR scenarios
    python 39_federal_ethics_gift_gate.py --standard  # skip the verified profile
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "gift_acceptance_cases.csv"

DOMAIN_NAME = "Federal gift-acceptance ethics gate (5 CFR 2635 Subpart B)"
DOMAIN_DESCRIPTION = (
    "Decide whether a federal executive-branch employee may accept an offered gift; the outcome "
    "is permit, decline, or escalate. Each gift has a market_value in dollars, an "
    "aggregate_value_this_source_occasion (total dollars offered by this source on this occasion) "
    "in dollars, an annual_aggregate_this_source (total dollars accepted from this source this "
    "calendar year including this gift) in dollars, and the flags is_cash_or_investment (the gift "
    "is cash or an investment interest such as stock, bonds, certificates of deposit, or a "
    "financial-institution gift card), conditioned_on_official_action (the gift is offered in "
    "return for or conditioned on an official action by the employee), unsolicited, "
    "is_excluded_item (the item is not a restricted gift: modest refreshments not offered as part "
    "of a meal, a "
    "greeting card or item of little intrinsic value, a commercial discount available to the "
    "general public, or an item for which the employee pays full market value), and "
    "raises_appearance_concern (the decision turns on a reasonable-person judgment such as an "
    "appearance of influence, suspicious timing, uncertain motivation, or an implausible value "
    "estimate). "
    "Classify these named conditions: the gift is a bribe when conditioned_on_official_action is "
    "true; the gift is a cash equivalent when is_cash_or_investment is true; the gift needs a "
    "judgment call when raises_appearance_concern is true; the gift is an excluded item when "
    "is_excluded_item is true; the gift qualifies for the small-gift exception when unsolicited "
    "is true and aggregate_value_this_source_occasion is at most 20 and "
    "annual_aggregate_this_source "
    "is at most 50. "
    "Decide the outcome by the first matching rule: decline when the gift is a bribe; decline "
    "when the gift is a cash equivalent; escalate when the gift needs a judgment call; permit "
    "when the "
    "gift is an excluded item; permit when the gift qualifies for the small-gift exception; "
    "otherwise decline."
)


def _facts(value, occ, annual, cash=False, bribe=False, unsolicited=True,
           excluded=False, appearance=False) -> dict:
    return {
        "market_value": value, "aggregate_value_this_source_occasion": occ,
        "annual_aggregate_this_source": annual, "is_cash_or_investment": cash,
        "conditioned_on_official_action": bribe, "unsolicited": unsolicited,
        "is_excluded_item": excluded, "raises_appearance_concern": appearance,
    }


# (label, expected verdict, facts) — rows are the CFR's own worked examples with ground-truth.
SHOWCASE = [
    ("1. $15 gift card conditioned on a product recommendation (bribery override)",
     "decline", _facts(15, 15, 15, bribe=True)),
    ("2. $15 retail coffee-chain gift card from a contractor at a holiday party",
     "permit", _facts(15, 15, 15)),
    ("3. $15 financial-institution gift card (cash equivalent)",
     "decline", _facts(15, 15, 15, cash=True)),
    ("4a. Trade show, Co. X software $15 (one source, <=$20)", "permit", _facts(15, 15, 15)),
    ("4b. Trade show, Co. Y calendar $12 (distinct source, <=$20)", "permit", _facts(12, 12, 12)),
    ("4c. Trade show, Co. Z deli lunch $8 (distinct source, <=$20)", "permit", _facts(8, 8, 8)),
    ("5a. One source, one occasion: framed map $18 AND mug $15 = $33 (accept both)",
     "decline", _facts(33, 33, 33)),
    ("5b. Same source/occasion: accept just the $18 map (<=$20 subset)",
     "permit", _facts(18, 18, 18)),
    ("6. Four $10 gifts across the year from one source, total $40 (<=$50 annual)",
     "permit", _facts(10, 10, 40)),
    ("6b. A further gift taking the annual total to $60 from that source (>$50)",
     "decline", _facts(10, 10, 60)),
    ("7. Two theater tickets, face value $30 each = $60, regulated entity (cannot pay down)",
     "decline", _facts(60, 60, 60)),
    ("8. Portable music player, market value $25, donor logo (real independent use)",
     "decline", _facts(25, 25, 25)),
    ("9. Sub-$20 lunch right after a promotional pitch; timing suggests influence",
     "escalate", _facts(15, 15, 15, appearance=True)),
    ("10. A greeting card of little intrinsic value (excluded — not a restricted gift)",
     "permit", _facts(3, 3, 3, excluded=True)),
]


def _decide(api, pid: int, label: str, expected: str, facts: dict) -> bool:
    try:
        report = api.platforms.query(pid, query="May the employee accept this gift?", facts=facts)
    except Exception as exc:  # a verified fail-safe refusal is an outcome, not a crash
        print(f"  {label}\n    VERIFIED FAIL-SAFE — refused to certify: {exc}")
        return False
    outcome = str(report.get("decision"))
    ok = outcome == expected
    mark = "OK" if ok else f"!! expected {expected}"
    pc = report.get("proof_checked")
    print(f"  {label}\n    -> {outcome.upper():8s} [{mark}]  proof_checked={pc}")
    return ok


def run_gift_gate(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Creating the gift-acceptance ethics domain (5 CFR 2635 B)")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology (classify-then-conclude gate)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=16)

    print_section(3, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    print(f"  Platform {pid}: {platform['name']} ({platform.get('status')})")

    print_section(4, total, "Deciding the CFR scenarios (each verdict proof-carrying)")
    correct = 0
    for label, expected, facts in SHOWCASE:
        correct += _decide(api, pid, label, expected, facts)
    print(f"\n{correct}/{len(SHOWCASE)} scenarios decided as the CFR requires. Platform {pid}. "
          "Bright-line cases are certified; the appearance-judgment case escalates to a human.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Federal gift-acceptance ethics gate (5 CFR 2635 Subpart B) — AmberTrace AI "
                    "verified permit/decline/escalate, each verdict proof-carrying. Illustrative "
                    "encoding for demonstration — not legal advice, not affiliated with any agency.")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: gift_acceptance_cases.csv)")
    args = parser.parse_args()
    run_demo(run_gift_gate, args)


if __name__ == "__main__":
    main()
