"""28 — Medical Device QMS Nonconformance Triage.

Creates a medical-device quality-management-system domain (ISO 13485 / FDA
CAPA), uploads nonconformance records, builds the ontology and platform, and
runs queries designed to trigger triage rules (critical/safety defects,
sterility breaches, regulatory-reportable failures, recurring nonconformances).
Every answer comes back as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 28_medical_device_qms.py
    python 28_medical_device_qms.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "device_nonconformances.csv"

DOMAIN_NAME = "Medical Device QMS Nonconformance Triage"
DOMAIN_DESCRIPTION = (
    "Nonconformance triage for a medical device quality management system under "
    "ISO 13485 and FDA CAPA requirements. The domain enforces the following rules: "
    "a critical-severity or safety-affecting nonconformance requires a CAPA; "
    "a sterility-affecting nonconformance requires a field action; "
    "a regulatory-reportable nonconformance must be escalated for field action; "
    "a nonconformance with a recurrence_count of 3 or more requires a CAPA; "
    "minor isolated nonconformances are recorded as minor deviations. "
    "All decisions must be auditable and explainable for regulatory compliance."
)

QMS_QUERIES = [
    "A final_qc inspection found a critical defect on infusion pump batch "
    "BATCH-204 that affects patient safety. What triage outcome applies?",
    "A sterility breach was detected on surgical kit batch BATCH-118. The "
    "nonconformance affects sterility. How should this be handled?",
    "A minor cosmetic labelling defect on catheter line has now occurred for "
    "the third time (recurrence_count 3). What outcome does this require?",
    "Evaluate a one-off minor cosmetic scratch found at incoming inspection "
    "with no safety, sterility, or complaint impact. How is it recorded?",
    "A field failure on dialysis machine batch BATCH-301 is regulatory "
    "reportable. What escalation and field action are required?",
    "What rules and thresholds does the platform use to triage device "
    "nonconformances?",
]


def run_qms_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or QMS_QUERIES
    total = 7

    print_section(1, total, "Creating medical device QMS domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading device nonconformance data")
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

    print_section(7, total, "Running nonconformance triage queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Medical Device QMS Nonconformance Triage — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: device_nonconformances.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample QMS queries.",
    )
    args = parser.parse_args()
    run_demo(run_qms_demo, args)


if __name__ == "__main__":
    main()
