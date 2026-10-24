"""72 -- decision_posture: what a query that matches NO verdict rule returns.

A Decisions platform fails CLOSED by default. When a query lands in a region none
of your verdict rules covers (e.g. rules say "deny if risk > 80" and "permit if
risk < 20", and the query has risk = 50) the served answer is ``status ==
"abstain"`` with ``decision`` None and ``permitted`` False -- a gap in your rules
never silently approves.

If your policy genuinely is "allow unless a rule says otherwise", declare it when
you build the platform:

    api.platforms.create(domain_id=..., dataset_id=..., decision_posture="default_allow")

``decision_posture`` is ``"fail_closed"`` (the default when omitted) or
``"default_allow"``. With ``default_allow`` an uncovered query is served the
decision table's default outcome (e.g. ``permit``). The posture is only ever what
you declare; it is never inferred from your verbs or table.

This script builds the same domain twice -- default and ``default_allow`` -- and
queries the uncovered point on both, on the bundled lending CSV.

Creates resources on your account. Run with --help for options.

    python 74_decision_posture.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    create_domain,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

DOMAIN_DESCRIPTION = (
    "Lending screening for personal loans. An application is denied when the "
    "debt_to_income_ratio is above 0.60, and approved when the debt_to_income_ratio "
    "is below 0.20. Decide each application: deny or approve."
)
DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "deny", "order": 2, "permits": False, "values": ["denied"]},
        {"label": "approve", "order": 1, "default": True, "permits": True,
         "values": ["approved"]},
    ],
}
# Between the two thresholds: no verdict rule covers it.
UNCOVERED_FACTS = {"debt_to_income_ratio": 0.40}


def _build(api, args, posture):
    domain = create_domain(
        api, name=f"Decision posture demo ({posture or 'default'})",
        description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    api.domains.set_decision_table(domain["id"], DECISION_TABLE)
    domain = build_ontology(api, domain["id"])
    extra = {"decision_posture": posture} if posture else {}
    return build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau, **extra)


def run_posture(api, args: argparse.Namespace) -> None:
    for posture in (None, "default_allow"):
        platform = _build(api, args, posture)
        report = api.platforms.query(
            platform["id"], query="What is the lending decision?",
            facts=UNCOVERED_FACTS)
        print(f"\n  decision_posture={posture or 'fail_closed (default)'}")
        print(f"    decision:  {report.get('decision')}")
        print(f"    permitted: {report.get('permitted')}")
        print(f"    status:    {report.get('status')}")
    print("\nDone. fail_closed abstains on the uncovered query; default_allow permits it.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="decision_posture -- fail-closed vs default_allow on an uncovered query")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="CSV file to upload (default: loan_applications.csv)")
    args = parser.parse_args()
    run_demo(run_posture, args)


if __name__ == "__main__":
    main()
