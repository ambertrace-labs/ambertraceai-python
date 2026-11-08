"""76 -- a combined-total rule: "the combined total of A, B exceeds P percent of C".

A decision rule can compare the SUM of several columns against a share of another
column. Say it in the domain description in this form::

    the combined total of monthly payment, exposure exceeds 60 percent of the
    monthly income

(``total of`` and ``sum of`` work too; list the columns with commas or "and";
"must not exceed" / "at most" state the same bound from the compliant side.) The
platform adds the sum as a derived column, enforces ``payment + exposure > 0.6 x
income`` as ONE verdict rule, and keeps every other clause of the sentence -- an
unreadable clause in an "or" is dropped on its own instead of discarding the
rest of the rule.

Behaviour worth knowing:

  * strict sum -- a query that does not carry EVERY listed column gets no total
    (never a partial sum), so the bound simply does not fire for it;
  * the bound is exclusive -- a total exactly at P percent is NOT "exceeds";
  * list the columns by their data-column names (spaces for underscores is fine).

Creates resources on your account. Run with --help for options.

    python 76_combined_total_rule.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    create_domain,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "exposure_applications.csv"

DOMAIN_DESCRIPTION = (
    "Decide deny if clearance_ok is false, or if the combined total of monthly "
    "payment, exposure exceeds 60 percent of the monthly income. Otherwise "
    "decide approve."
)

DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "deny", "order": 2, "permits": False},
        {"label": "approve", "order": 1, "default": True, "permits": True},
    ],
}

# (clearance_ok, monthly_income, monthly_payment, exposure) -> expected decision
CASES: list[tuple[dict[str, Any], str]] = [
    ({"clearance_ok": False, "monthly_income": 4000,
      "monthly_payment": 800, "exposure": 600}, "deny"),
    ({"clearance_ok": True, "monthly_income": 4000,
      "monthly_payment": 1500, "exposure": 1000}, "deny"),      # 2500 > 2400
    ({"clearance_ok": True, "monthly_income": 4000,
      "monthly_payment": 1200, "exposure": 1200}, "approve"),   # == 2400: not exceeds
    ({"clearance_ok": True, "monthly_income": 8000,
      "monthly_payment": 1500, "exposure": 1000}, "approve"),   # 2500 <= 4800
]


def run_combined_total(api, args: argparse.Namespace) -> None:
    print_section(1, 4, "Creating the domain (the combined-total rule is in the description)")
    domain = create_domain(
        api, name="Combined-total exposure check", description=DOMAIN_DESCRIPTION,
        decision_table=DECISION_TABLE)
    print(f"  Domain {domain['id']}")

    print_section(2, 4, "Uploading data and building the ontology")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    domain = build_ontology(api, domain["id"])

    print_section(3, 4, "Building the verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
        decision_posture="default_allow")
    print(f"  Platform {platform['id']}")

    print_section(4, 4, "Querying with structured facts")
    for facts, expected in CASES:
        result = api.platforms.query(
            platform["id"], query="Decide this application", facts=facts)
        print(f"  {facts} -> {result.get('decision')!r} (expected {expected!r})")


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Combined-total rule -- "the combined total of A, B exceeds P percent of C"')
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="CSV file to upload (default: exposure_applications.csv)")
    args = parser.parse_args()
    run_demo(run_combined_total, args)


if __name__ == "__main__":
    main()
