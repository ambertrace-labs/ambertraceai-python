"""13 — Loan Approval Assessment.

Creates a lending domain with regulatory constraints, uploads loan
application data, builds the ontology and platform, and runs queries
designed to trigger symbolic rules (DTI thresholds, age restrictions,
credit score minimums). The Amber Reports demonstrate explainability
required by financial regulators.

Creates resources on your account. Run with --help for options.

    python 13_loan_assessment.py
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
    print_graph,
    print_ontology,
    print_quality,
    print_section,
    query_and_report,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

DOMAIN_NAME = "Loan Approval Assessment"
DOMAIN_DESCRIPTION = (
    "Lending risk assessment for personal and secured loans. "
    "The domain enforces regulatory compliance rules including: "
    "applicants must be 18 or older; debt-to-income ratio must not exceed 43%; "
    "minimum credit score thresholds apply per loan tier; "
    "employment verification is required. "
    "All decisions must be explainable and auditable for fair lending compliance."
)

LOAN_QUERIES = [
    "Should we approve a loan for an applicant with annual income £28,000, "
    "debt-to-income ratio 0.46, credit score 610, age 25, who wants £6,500 for personal use?",
    "Can a 17-year-old with no income apply for a £3,000 personal loan?",
    "Evaluate a loan application: 45-year-old homeowner, £78,000 income, "
    "credit score 760, DTI ratio 0.15, employed 12 years, "
    "requesting £25,000 for home improvement.",
    "What is the risk assessment for an applicant with credit score 580, "
    "income £24,000, and 3 existing loans seeking debt consolidation?",
    "What rules determine whether a loan application is approved or denied?",
]


def run_loan_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or LOAN_QUERIES
    total = 7

    print_section(1, total, "Creating lending domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading loan application data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (generating entities & rules)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(4, total, "Checking data quality")
    print_quality(api.datasets.quality(dataset["id"]))

    print_section(5, total, "Building platform (knowledge graph + rule engine)")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(6, total, "Exploring knowledge graph")
    print_graph(api.platforms.graph(platform["id"]))

    print_section(7, total, "Running loan assessment queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Loan Approval Assessment — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: loan_applications.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample loan queries.",
    )
    args = parser.parse_args()
    run_demo(run_loan_demo, args)


if __name__ == "__main__":
    main()
