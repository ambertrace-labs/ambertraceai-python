"""30 — ESG / CSRD Sustainability Disclosure Completeness Check.

Creates an ESG-disclosure domain, uploads sustainability disclosure data,
builds the ontology and platform, and runs queries designed to trigger
disclosure-completeness rules (missing materiality assessment, missing Scope 3
under CSRD, missing assurance, excessive data gaps, missing double materiality).
Every decision comes back as an Amber Report — auditable for regulatory review.

Creates resources on your account. Run with --help for options.

    python 30_esg_disclosure_check.py
    python 30_esg_disclosure_check.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "esg_disclosures.csv"

DOMAIN_NAME = "ESG / CSRD Disclosure Completeness Check"
DOMAIN_DESCRIPTION = (
    "Sustainability disclosure completeness checking that classifies each "
    "reporting entity's disclosure as compliant, incomplete, or non_compliant "
    "across the CSRD, GRI, and ISSB frameworks. The domain enforces the "
    "following rules: "
    "a disclosure with no materiality assessment is non-compliant; "
    "under the CSRD framework a disclosure missing scope3_reported is incomplete; "
    "a disclosure with an assurance_level of none is incomplete; "
    "a disclosure with a data_gaps_count above 5 is incomplete; "
    "a CSRD disclosure must use double materiality, and one that does not is "
    "non-compliant; "
    "an otherwise complete, assured disclosure is compliant. "
    "All decisions must be auditable and explainable for regulatory review."
)

ESG_QUERIES = [
    "A CSRD report from Northwind Energy reports Scope 1 and Scope 2 but is "
    "missing Scope 3. Is this disclosure complete?",
    "A disclosure was filed with no materiality assessment done. "
    "How should this report be classified?",
    "An unassured GRI report has an assurance_level of none but is otherwise "
    "complete. Is this compliant?",
    "A report has a data_gaps_count of 9. Does this affect its disclosure "
    "completeness status?",
    "A CSRD report has Scope 1, 2, and 3, reasonable assurance, a completed "
    "double-materiality assessment, and zero data gaps. Is it compliant?",
    "What rules and thresholds does the platform use to decide whether a "
    "disclosure is compliant, incomplete, or non-compliant?",
]


def run_esg_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or ESG_QUERIES
    total = 7

    print_section(1, total, "Creating ESG disclosure domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading ESG disclosure data")
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

    print_section(7, total, "Running disclosure completeness queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ESG / CSRD Disclosure Completeness Check — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: esg_disclosures.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample disclosure queries.",
    )
    args = parser.parse_args()
    run_demo(run_esg_demo, args)


if __name__ == "__main__":
    main()
