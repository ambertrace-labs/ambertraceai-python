"""27 — AML Transaction Monitoring.

Creates an anti-money-laundering domain, uploads transaction monitoring data,
builds the ontology and platform, and runs queries designed to trigger AML
rules (sanctions hits, high-risk jurisdictions, structuring patterns, PEP
involvement). Every answer comes back as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 27_aml_transaction_monitoring.py
    python 27_aml_transaction_monitoring.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "aml_transactions.csv"

DOMAIN_NAME = "AML Transaction Monitoring"
DOMAIN_DESCRIPTION = (
    "Anti-money-laundering transaction monitoring across retail, wire, and card "
    "channels. The domain enforces the following rules: "
    "any transaction with a sanctions hit must be reported; "
    "transactions to high country_risk jurisdictions must be flagged for review; "
    "multiple sub-threshold transactions whose cumulative_24h_amount exceeds 10000 "
    "within 24 hours (structuring) must be flagged; "
    "transactions involving a PEP must be flagged for enhanced due diligence; "
    "normal low-risk transactions are cleared. "
    "All decisions must be auditable and explainable for regulatory compliance."
)

AML_QUERIES = [
    "A wire transfer of $48,000 to counterparty CP-204 returned a sanctions "
    "screening hit. Should this transaction be reported?",
    "Account ACC-007 made 6 transfers under $3,000 each in one day, totalling "
    "$15,200 in cumulative_24h_amount. Is this a structuring pattern?",
    "A $90,000 wire is being sent on behalf of a politically exposed person "
    "(PEP). What enhanced due diligence applies?",
    "Evaluate a routine $85 retail card purchase from a low-risk domestic "
    "merchant for account ACC-001. Should it be cleared?",
    "A $22,000 payment is heading to counterparty CP-220 in a high country_risk "
    "jurisdiction. How should this transaction be handled?",
    "What rules and thresholds does the platform use to monitor transactions "
    "for money laundering?",
]


def run_aml_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or AML_QUERIES
    total = 7

    print_section(1, total, "Creating AML transaction monitoring domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading transaction monitoring data")
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

    print_section(7, total, "Running AML monitoring queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="AML Transaction Monitoring — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: aml_transactions.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample AML queries.",
    )
    args = parser.parse_args()
    run_demo(run_aml_demo, args)


if __name__ == "__main__":
    main()
