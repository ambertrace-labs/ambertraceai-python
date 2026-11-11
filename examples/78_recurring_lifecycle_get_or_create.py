"""78 — Recurring lifecycle: build once, reuse forever (get_or_create).

A scheduled job that runs ``domains.create`` -> upload -> build every night mints a
brand-new domain, dataset and platform per run -- thousands of near-identical copies
within a year. Build the triple ONCE and look it up on every later run:

  1. ``domains.get_or_create(name=...)`` -- idempotent: the same name returns the
     SAME domain (``created`` is True only the first time). ``ensure`` is an alias.
  2. Reuse the domain's dataset if it has one (``datasets.list(domain_id=...)``);
     upload only on the first run. For a connector fetch,
     ``datasets.get_or_create(domain_id=, connector_type=, config=)`` does the same
     lookup by connector + config.
  3. Reuse the domain's active platform (``platforms.list(domain_id=, status=...)``);
     build only when there is none. ``platforms.get(id)["dataset_ids"]`` names the
     datasets it was built from.
  4. Query the platform -- the recurring part of the job.

Run it twice: the second run creates nothing and prints the same ids.

    python 78_recurring_lifecycle_get_or_create.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

DOMAIN_NAME = "Recurring lending screen (reusable)"
DOMAIN_DESCRIPTION = (
    "Lending screening for personal loans. An application is declined when the applicant_age "
    "is below 18, when the debt_to_income_ratio is above 0.43, or when the credit_score is "
    "below 600. Decide each application: deny or approve; approve it otherwise."
)
FACTS = {"applicant_age": 34.0, "credit_score": 710.0, "debt_to_income_ratio": 0.25}


def run_lifecycle(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Get or create the domain (idempotent)")
    domain = api.domains.get_or_create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    again = api.domains.get_or_create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']} created={domain['created']}; "
          f"second call -> {again['id']} created={again['created']} (same id)")

    print_section(2, total, "Reuse the dataset, upload only when there is none")
    datasets = api.datasets.list(domain_id=domain["id"])
    if datasets:
        dataset = datasets[0]
        print(f"  Reusing dataset {dataset['id']} ({len(datasets)} on this domain)")
    else:
        dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
        print(f"  Uploaded dataset {dataset['id']}")

    print_section(3, total, "Reuse the active platform, build only when there is none")
    platforms = api.platforms.list(domain_id=domain["id"], status="active")
    if platforms:
        platform = platforms[0]
        print(f"  Reusing platform {platform['id']} (domain_name={platform.get('domain_name')!r})")
    else:
        if domain["created"] or domain.get("status") == "draft":
            build_ontology(api, domain["id"])
        platform = build_platform(
            api, domain["id"], dataset["id"],
            verified_profile=not args.standard,
            verified_min_confidence=args.tau,
            decision_posture="default_allow",
        )
        print(f"  Built platform {platform['id']}")
    detail = api.platforms.get(platform["id"])
    print(f"  Built from dataset ids: {detail.get('dataset_ids')}")

    print_section(4, total, "Query -- the part you repeat on every run")
    report = api.platforms.query(
        platform["id"], query="What is the lending decision?", facts=FACTS)
    print(f"  decision={report.get('decision')} permitted={report.get('permitted')} "
          f"status={report.get('status')}")
    print(f"\nDone. Run again: domain {domain['id']} / platform {platform['id']} are reused.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recurring lifecycle -- build once, reuse with get_or_create",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="CSV file to upload on the first run (default: loan_applications.csv)")
    args = parser.parse_args()
    run_demo(run_lifecycle, args)


if __name__ == "__main__":
    main()
