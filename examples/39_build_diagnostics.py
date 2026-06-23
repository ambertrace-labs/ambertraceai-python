"""39 — Platform build diagnostics.

Walks a platform build end-to-end and reads the build job's
`result.generation_diagnostics` — what rule generation produced and whether
the rule set can ever reach an adverse (deny/block) decision. Because
_common.build_platform returns the platform (not the build job), this demo
calls api.platforms.create directly to capture the build job's result.

  1. Create a small permit/deny PDP domain
  2. Upload access-request data
  3. Build the ontology
  4. Create the platform and capture the build_job id
  5. Read & interpret generation_diagnostics (+ build_quality)

Creates resources on your account. Run with --help for options.

    python 39_build_diagnostics.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "access_requests.csv"

# A short, self-contained permit/deny PDP so the generated rule set CAN reach
# an adverse decision (deny conclusions present). Duplicated intentionally —
# not imported from example 18.
DOMAIN_NAME = "Build Diagnostics PDP"
DOMAIN_DESCRIPTION = (
    "Access-governance Policy Decision Point. Each request has a clearance level from 1 to 4, "
    "whether the device is managed, a device posture score from 0 to 100, whether MFA passed, "
    "a target zone, a target sensitivity from 1 to 4, and an access type. "
    "Classify these named conditions: a device is trusted when it is managed and its posture "
    "score is at least 70; a request is privileged when the access type is write or admin. "
    "Decide permit or deny by the first matching rule: deny for untrusted device when the target "
    "zone is the restricted zone and the device is not trusted; deny for mfa required when the "
    "request is privileged and MFA did not pass; deny for insufficient clearance when the "
    "clearance level is below the target sensitivity; otherwise permit. Every decision must be "
    "auditable."
)


def _print_diagnostics(diag: dict) -> None:
    """Print every documented generation_diagnostics field."""
    print(f"  rule_count:                 {diag.get('rule_count')}")
    print(f"  classifier_count:           {diag.get('classifier_count')}")
    print(f"  verdict_conclusion_count:   {diag.get('verdict_conclusion_count')}")
    print(f"  connected_restrictive_count:{diag.get('connected_restrictive_count')}")
    print(f"  can_decide_adversely:       {diag.get('can_decide_adversely')}")
    print(f"  decision_coverage_warnings: {diag.get('decision_coverage_warnings')}")
    print(f"  non_discriminating_rules:   {diag.get('non_discriminating_rules')}")
    print(f"  orphan_derived:             {diag.get('orphan_derived')}")
    print(f"  unbound_references:         {diag.get('unbound_references')}")


def run_build_diagnostics_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating permit/deny PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading access-request data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (classify-then-conclude chain)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(4, total, "Creating platform & capturing build job")
    resp = api.platforms.create(
        domain_id=domain["id"], dataset_id=dataset["id"], verified_profile=False,
    )
    build_job = resp.get("build_job") or {}
    build_job_id = build_job.get("id") or resp.get("job_id")
    if build_job_id is None:
        print(
            "  ERROR: platform creation returned no build_job id — cannot read\n"
            f"  build diagnostics. Response keys: {sorted(resp)}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"  build_job id = {build_job_id} — polling for the build result...")
    job = api.wait_for_job(int(build_job_id), timeout=600)
    print(f"  Build job finished with status: {job.get('status')}")

    print_section(5, total, "Build diagnostics (generation_diagnostics)")
    result = job.get("result") or {}
    diag = result.get("generation_diagnostics", {}) or {}
    if not diag:
        print("  No generation_diagnostics on this build job's result.")
    else:
        _print_diagnostics(diag)
        # README interpretation: verdict_conclusion_count == 0 means the rule
        # set classifies inputs but never concludes deny/block — it permits
        # everything and can never refuse.
        if not diag.get("can_decide_adversely", True):
            print("\n  Platform reaches no adverse decision:")
            for w in diag.get("decision_coverage_warnings", []):
                print(f"    - {w}")
        else:
            print("\n  Rule set can reach an adverse (deny/block) decision.")

    quality = result.get("build_quality")
    if quality is not None:
        print(f"\n  build_quality: {quality}")

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Platform build diagnostics — AmberTrace AI SDK mechanics demo",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_build_diagnostics_demo, args)


if __name__ == "__main__":
    main()
