"""29 — Trust & Safety Content Moderation.

Creates a content-moderation domain, uploads moderation decision data, builds
the ontology and platform, and runs queries designed to trigger moderation
rules (CSAM removal, hate-speech removal, violence/self-harm limits, repeat-
offender escalation). Every decision comes back as an Amber Report — auditable
and explainable to the user, per DSA-style transparency requirements.

Creates resources on your account. Run with --help for options.

    python 29_content_moderation.py
    python 29_content_moderation.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "content_moderation.csv"

DOMAIN_NAME = "Trust & Safety Content Moderation"
DOMAIN_DESCRIPTION = (
    "Explainable trust & safety content moderation deciding whether each item is "
    "allowed, limited (reduced distribution), or removed across posts, comments, "
    "videos, and images. The domain enforces the following rules: "
    "any item with a CSAM flag must be removed and reported immediately; "
    "an item with a hate_score of at least 0.8 must be removed; "
    "an item with a violence_score or self_harm_score of at least 0.7 must be "
    "limited with reduced distribution; "
    "content from a repeat offender escalates a limit to a removal; "
    "otherwise the item is allowed. "
    "All decisions must be auditable and explainable to the user, per DSA-style "
    "transparency requirements."
)

MODERATION_QUERIES = [
    "An image upload came in with a CSAM flag set and a low hate score. "
    "What action should be taken on this item?",
    "A post has a hate_score of 0.88 and was reported by 6 users. "
    "Should this content be removed?",
    "A video has a self_harm_score of 0.72 from a first-time poster with no "
    "prior violations. How should this borderline item be handled?",
    "A monetized post has a hate_score of 0.05, a violence_score of 0.02, and "
    "zero reports. What moderation outcome applies?",
    "A repeat offender posted a comment with a violence_score of 0.74. "
    "Should this be limited or removed?",
    "What rules and thresholds does the platform use to decide whether content "
    "is allowed, limited, or removed?",
]


def run_moderation_demo(api, args: argparse.Namespace) -> None:
    queries = args.queries or MODERATION_QUERIES
    total = 7

    print_section(1, total, "Creating content moderation domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading content moderation data")
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

    print_section(7, total, "Running moderation decision queries")
    for query in queries:
        query_and_report(api, platform["id"], query)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trust & Safety Content Moderation — AmberTrace AI explainability demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: content_moderation.csv)",
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Custom query (repeatable). Defaults to sample moderation queries.",
    )
    args = parser.parse_args()
    run_demo(run_moderation_demo, args)


if __name__ == "__main__":
    main()
