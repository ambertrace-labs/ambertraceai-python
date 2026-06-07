"""15 — Environmental Regulatory Compliance.

Creates an environmental monitoring domain, uploads facility emission
data, builds the ontology and platform, and runs queries designed to
trigger compliance rules (regulatory/permit limit breaches, missing
permits, inspector verification, protected-zone enforcement). Every
answer comes back as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 15_environmental_compliance.py
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
DEFAULT_DATASET = DATA_DIR / "environmental_monitoring.csv"

DOMAIN_NAME = "Environmental Regulatory Compliance"
DOMAIN_DESCRIPTION = (
    "Environmental monitoring and regulatory compliance for industrial facilities. "
    "The domain enforces the following rules: "
    "emission readings must not exceed the regulatory limit for the pollutant "
    "(measurement_value must be less than or equal to regulatory_limit); "
    "emission readings must not exceed the facility's permit limit "
    "(measurement_value must be less than or equal to permit_limit); "
    "facilities must have an active environmental permit to operate "
    "(permit_active must be Yes); "
    "readings must be verified by an inspector before compliance status is confirmed "
    "(inspector_verified must be Yes); "
    "facilities in coastal_protected zones have stricter limits and any breach "
    "requires immediate enforcement action; "
    "facilities in urban_residential zones must not exceed regulatory limits "
    "for any pollutant; "
    "three or more consecutive breaches by the same facility triggers licence suspension; "
    "all compliance decisions must be auditable for environmental regulatory reporting."
)

ENVIRONMENTAL_QUERIES = [
    "Riverside Chemical Works recorded nitrogen dioxide at 44.8 ug/m3 against "
    "a regulatory limit of 40.0 ug/m3. Is this facility in breach?",
    "Northern Steel Mill measured particulate matter at 46.8 ug/m3. The permit "
    "limit is 45.0 ug/m3 and the regulatory limit is 50.0 ug/m3. What is the "
    "compliance status?",
    "Dockside Recycling has no active environmental permit but is still "
    "operating and recording methane emissions. Is this legal?",
    "A facility has readings that exceed regulatory limits but the readings "
    "have not been verified by an inspector. Can enforcement action be taken?",
    "Coastal Refinery measured benzene at 6.5 ug/m3 in a coastal protected zone. "
    "The regulatory limit is 5.0 ug/m3. What enforcement action is required?",
    "Greenway Biotech recorded volatile organic compounds at 88.0 ug/m3 against "
    "a permit limit of 120.0 ug/m3 and regulatory limit of 150.0 ug/m3. "
    "The facility has an active permit and readings are inspector-verified. "
    "Is this facility compliant?",
    "What rules and thresholds determine whether a facility is in breach of "
    "environmental regulations?",
]


def run_environmental_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or ENVIRONMENTAL_QUERIES
    total = 7

    print_section(1, total, "Creating environmental compliance domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading facility monitoring data")
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

    print_section(7, total, "Running environmental compliance queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Environmental Regulatory Compliance — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: environmental_monitoring.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample environmental queries.",
    )
    args = parser.parse_args()
    run_demo(run_environmental_demo, args)


if __name__ == "__main__":
    main()
