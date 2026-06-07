"""11 — Insurance Claims Fraud Detection.

Creates a fraud-detection domain, uploads insurance claim data, builds the
ontology and platform, and runs queries designed to trigger fraud rules
(policy-limit breaches, early claims, high claim frequency, provider
collusion). Every answer comes back as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 11_fraud_detection.py
    python 11_fraud_detection.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "insurance_claims.csv"

DOMAIN_NAME = "Insurance Claims Fraud Detection"
DOMAIN_DESCRIPTION = (
    "Fraud detection and risk assessment for insurance claims across auto, property, "
    "and medical lines. The domain enforces the following rules: "
    "claims exceeding the policy limit must be denied; "
    "claims filed within 90 days of policy start date must be flagged for review; "
    "claimants with 4 or more previous claims must be flagged as high-frequency; "
    "claims exceeding 90% of the policy limit must be flagged as high amount ratio; "
    "providers appearing on multiple flagged claims must be investigated for collusion. "
    "All decisions must be auditable and explainable for regulatory compliance."
)

FRAUD_QUERIES = [
    "A claimant is filing a property flood claim for £55,000 on a policy "
    "with a £50,000 limit. Should this claim be approved?",
    "Claimant took out a policy on October 2nd and filed an £11,500 property "
    "flood claim on October 20th — just 18 days later. Is this suspicious?",
    "Claimant CLT-008 has filed 6 medical claims in 18 months through "
    "provider PRV-015. What is the fraud risk assessment?",
    "Provider PRV-011 appears on 7 property fire claims. Is there evidence "
    "of provider collusion or fraud patterns?",
    "Evaluate a standard auto collision claim: £4,500 on a £50,000 policy, "
    "claimant has zero previous claims, policy started 14 months ago.",
    "What rules and thresholds does the platform use to detect fraudulent claims?",
]


def run_fraud_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or FRAUD_QUERIES
    total = 7

    print_section(1, total, "Creating fraud detection domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading insurance claims data")
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

    print_section(7, total, "Running fraud assessment queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Insurance Claims Fraud Detection — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: insurance_claims.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample fraud queries.",
    )
    args = parser.parse_args()
    run_demo(run_fraud_demo, args)


if __name__ == "__main__":
    main()
