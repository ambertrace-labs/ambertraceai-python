"""14 — HR Recruitment Compliance.

Creates a recruitment compliance domain, uploads candidate data, builds
the ontology and platform, and runs queries designed to trigger
compliance rules (minimum age, salary bands, right to work, reference
checks, bias detection). Every answer comes back as an Amber Report.

Creates resources on your account. Run with --help for options.

    python 13_recruitment_compliance.py
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
DEFAULT_DATASET = DATA_DIR / "recruitment_applications.csv"

DOMAIN_NAME = "HR Recruitment Compliance"
DOMAIN_DESCRIPTION = (
    "Recruitment decision compliance for hiring across all departments. "
    "The domain enforces the following rules: "
    "applicants must be 18 or older to be employed; "
    "salary expectations must fall within the role's published salary band "
    "(salary_expectation must be between role_salary_band_min and role_salary_band_max); "
    "qualifications must be relevant to the role applied for "
    "(qualification_relevant must be Yes); "
    "all candidates must have right to work in the UK (right_to_work must be Yes); "
    "reference checks must pass before hiring (reference_check must be Pass); "
    "skills match score must be at least 65 for shortlisting; "
    "hiring decisions must not correlate with gender, ethnicity, disability_status, "
    "or age — any rejection where interview_score is 0 and the candidate meets all "
    "objective criteria is flagged as potential bias; "
    "all hiring decisions must be explainable and auditable for equality compliance."
)

RECRUITMENT_QUERIES = [
    "Can we hire a 16-year-old applicant for a junior developer role?",
    "A senior developer candidate expects £95,000 but the role band is £65,000-£85,000. "
    "Should we proceed?",
    "An excellent candidate scored 88 on skills match but has no right to work "
    "in the UK. Can we hire them?",
    "A candidate with 14 years experience, PhD in Computer Science, and 96% skills "
    "match was rejected without interview. Is this compliant?",
    "Evaluate hiring a 33-year-old candidate with MSc Statistics, 8 years experience, "
    "86% skills match, interview score 80, passed references, right to work confirmed, "
    "salary expectation £49,000 within band £40,000-£55,000.",
    "What rules determine whether a recruitment decision is compliant with "
    "equality legislation?",
]


def run_recruitment_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or RECRUITMENT_QUERIES
    total = 7

    print_section(1, total, "Creating recruitment compliance domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading candidate application data")
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

    print_section(7, total, "Running recruitment compliance queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="HR Recruitment Compliance — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: recruitment_applications.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample recruitment queries.",
    )
    args = parser.parse_args()
    run_demo(run_recruitment_demo, args)


if __name__ == "__main__":
    main()
