"""12 — Clinical Prescribing Safety.

Creates a clinical decision-support domain, uploads prescription data,
builds the ontology and platform, and runs queries designed to trigger
safety rules (drug-drug interactions, contraindications, allergy
cross-reactions, elderly high-risk medications). Every answer comes back
as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 11_clinical_safety.py
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
DEFAULT_DATASET = DATA_DIR / "clinical_prescriptions.csv"

DOMAIN_NAME = "Clinical Prescribing Safety"
DOMAIN_DESCRIPTION = (
    "Clinical decision support for safe prescribing of medications. "
    "The domain enforces the following safety rules: "
    "drug-drug interactions must be flagged when two medications with a known "
    "interaction are prescribed to the same patient; "
    "duplicate drug class prescriptions must be flagged when a patient receives "
    "two medications from the same pharmacological class; "
    "contraindicated medications must be blocked when prescribed to patients "
    "with conditions that make the medication unsafe (e.g. NSAIDs with chronic "
    "kidney disease, metformin with severe renal impairment); "
    "allergy cross-reactions must be blocked when a medication is prescribed to "
    "a patient with an allergy to a related drug class (e.g. penicillin allergy "
    "contraindicates amoxicillin and may contraindicate cephalosporins); "
    "high-risk medications for elderly patients (age 80+) must be flagged for "
    "review, especially opioids and sedatives; "
    "age-restricted medications must be verified before prescribing to minors. "
    "All prescribing decisions must be auditable for patient safety compliance."
)

CLINICAL_QUERIES = [
    "A patient on warfarin for atrial fibrillation is being prescribed aspirin. Is this safe?",
    "Can we prescribe ibuprofen 400mg to an 82-year-old patient with "
    "osteoarthritis and chronic kidney disease?",
    "Patient has a documented penicillin allergy. Can we prescribe amoxicillin "
    "500mg for an infection?",
    "A patient on fluoxetine for depression is being started on paroxetine by "
    "a different doctor. Should this be allowed?",
    "Is it safe to prescribe tramadol 50mg to a 90-year-old patient with "
    "chronic pain and dementia?",
    "A patient taking nitroglycerin for angina wants a prescription for "
    "sildenafil. What are the risks?",
    "Evaluate a prescription for amlodipine 5mg daily for a 55-year-old "
    "patient with hypertension and type 2 diabetes. No allergies, no "
    "other medications.",
]


def run_clinical_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or CLINICAL_QUERIES
    total = 7

    print_section(1, total, "Creating clinical prescribing domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading prescription data")
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

    print_section(7, total, "Running clinical safety queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clinical Prescribing Safety — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: clinical_prescriptions.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample clinical queries.",
    )
    args = parser.parse_args()
    run_demo(run_clinical_demo, args)


if __name__ == "__main__":
    main()
