"""71 — Decision Table quickstart (data -> proposed table -> confirm -> build -> decide).

A platform decides over a DECISION TABLE: the outcomes a decision can take, each
with a ``label`` (your word, served verbatim in ``decision``), a precedence
``order``, whether it ``permits`` the action, one ``default`` row (the outcome when
nothing fires) and the data ``values`` that denote it. Three inputs must agree
before a platform builds: your DATA (mandatory), the domain DESCRIPTION, and the
decision table. You supply the data; the platform PROPOSES the other two from it and
you refine either.

This walkthrough follows that flow on a bundled lending CSV:

  1. Create a domain from a plain-English description (no table declared).
  2. Upload the CSV, then read ``datasets.quality(id)["decision_table"]``: the label
     column found, the table it PROPOSES from that column (with ``provenance`` and
     the fields it ``guessed``), and the consistency checks between data,
     description and table (C2 mapping errors BLOCK the build; C1/C3/C4/C6 are
     advisory warnings).
  3. Confirm or refine the table with ``domains.set_decision_table`` -- here mapping
     the CSV's ``approved`` / ``denied`` cells onto the labels ``approve`` / ``deny``
     via ``values``. (Nothing needs calling if the proposal is already right: a
     platform builds on the inferred table when the checks pass.)
  4. Build the ontology and platform; ``platforms.status`` echoes the table the
     platform was built with plus any advisory warnings.
  5. Query: branch on ``permitted`` to switch permit/deny, on ``decision`` for
     label-specific logic, on ``status`` for abstain / indeterminate / unavailable.

Creates resources on your account. Run with --help for options.

    python 71_decision_table_quickstart.py
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    create_domain,
    print_dataset,
    print_decision_checks,
    print_decision_table,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

DOMAIN_NAME = "Decision Table Quickstart (lending)"
DOMAIN_DESCRIPTION = (
    "Lending screening for personal loans. An application is declined when the applicant_age "
    "is below 18, when the debt_to_income_ratio is above 0.43, or when the credit_score is "
    "below 600. Decide each application: deny or approve; approve it otherwise."
)

# The refined table. `values` map the CSV's `outcome` cells onto these labels (exact,
# case-insensitive match; every distinct cell must map to exactly one row).
DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "deny", "order": 2, "permits": False, "values": ["denied"]},
        {"label": "approve", "order": 1, "default": True, "permits": True,
         "values": ["approved"]},
    ],
}

# Columns that are identifiers or the label itself, never query facts.
_NOT_FACTS = {"application_id", "application_date", "outcome", "denial_reason"}
_NUMERIC = {"applicant_age", "annual_income", "credit_score", "debt_to_income_ratio",
            "employment_years", "loan_amount", "existing_loans"}


def _facts(row: dict) -> dict:
    return {k: (float(v) if k in _NUMERIC else v)
            for k, v in row.items() if k not in _NOT_FACTS and v != ""}


def _sample_rows(path: Path) -> list[dict]:
    """The first approved and the first denied CSV row, as typed query facts."""
    wanted = {"approved", "denied"}
    out: list[dict] = []
    with path.open() as fh:
        for row in csv.DictReader(fh):
            if row["outcome"] in wanted:
                wanted.discard(row["outcome"])
                out.append(_facts(row))
            if not wanted:
                break
    return out


def run_quickstart(api, args: argparse.Namespace) -> None:
    total = 5

    print_section(1, total, "Creating the domain (no decision table declared)")
    domain = create_domain(api, name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} (decision_table={domain.get('decision_table')})")

    print_section(2, total, "Uploading data, reading the PROPOSED decision table")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)
    section = api.datasets.quality(dataset["id"]).get("decision_table") or {}
    label_column = section.get("label_column") or {}
    print(f"  Label column: {label_column.get('name')} ({label_column.get('source')})")
    print("  Table that applies now (inferred from the label column):")
    print_decision_table(section.get("table") or section.get("proposal"), indent="    ")
    print("  Consistency checks (blocking items stop the build; warnings are advisory):")
    print_decision_checks(section.get("checks"), indent="    ")
    if section.get("note"):
        print(f"  Note: {section['note']}")

    print_section(3, total, "Confirming the table with set_decision_table")
    stored = api.domains.set_decision_table(domain["id"], DECISION_TABLE)
    print_decision_table(stored, indent="  ")
    section = api.datasets.quality(dataset["id"]).get("decision_table") or {}
    print("  Checks after confirming:")
    print_decision_checks(section.get("checks"), indent="    ")

    print_section(4, total, "Building the ontology and platform")
    domain = build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
        # The description says "approve it otherwise": an allow-unless-a-rule-says-
        # otherwise policy.  Declare it -- the default is fail-closed (see 72).
        decision_posture="default_allow",
    )
    status = api.platforms.status(platform["id"])
    print(f"  Platform {platform['id']} ({status.get('status')}) built with table:")
    print_decision_table(status.get("decision_table"), indent="    ")
    for warning in status.get("decision_table_warnings") or []:
        print(f"    [warning] {warning.get('check', '?')}: {warning.get('message')}")

    print_section(5, total, "Deciding: decision / outcome / permitted / status")
    for facts in _sample_rows(args.dataset):
        report = api.platforms.query(
            platform["id"], query="What is the lending decision?", facts=facts)
        print(f"\n  facts: credit_score={facts.get('credit_score')} "
              f"dti={facts.get('debt_to_income_ratio')} age={facts.get('applicant_age')}")
        print(f"    decision:  {report.get('decision')}   (one of your labels)")
        print(f"    outcome:   {report.get('outcome')}   (permit iff the row permits)")
        print(f"    permitted: {report.get('permitted')}   (switch execute/block on this)")
        print(f"    status:    {report.get('status')}   (decided | abstain | indeterminate | unavailable)")
        if report.get("status") not in (None, "decided"):
            print("    -> no verdict reached: do not treat as approve OR deny")
        elif report.get("permitted"):
            print("    -> proceed")
        else:
            print("    -> blocked")

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Decision Table quickstart — data, proposed table, confirm, build, decide",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: loan_applications.csv)",
    )
    args = parser.parse_args()
    run_demo(run_quickstart, args)


if __name__ == "__main__":
    main()
