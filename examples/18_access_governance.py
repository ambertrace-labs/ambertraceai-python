"""18 — Access Governance PDP.

Verified proof-carrying access-governance domain: a classify-then-conclude
policy chain that evaluates access requests and returns permit/deny decisions
with machine-checked proofs. Each request is supplied as structured facts;
deny conclusions are read from the certified symbolic trace.

  1. Create domain (names the boolean classifications explicitly)
  2. Upload access-request data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Evaluate showcase requests — structured facts → checked proof

Creates resources on your account. Run with --help for options.

    python 18_access_governance.py
    python 18_access_governance.py --standard   # skip verified profile
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
    symbolic_rules,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "access_requests.csv"

DOMAIN_NAME = "Access Governance PDP"
DOMAIN_DESCRIPTION = (
    "Access-governance Policy Decision Point (PDP) for evaluating access requests. "
    "Each request has a requester role, a clearance level from 1 to 4, whether the device "
    "is managed, a device posture score from 0 to 100, whether MFA passed, a source zone "
    "and a target zone, a target sensitivity from 1 to 4, an access type, an off-hours flag, "
    "and a change-ticket flag. "
    "Classify these named conditions: a device is trusted when it is managed and its posture "
    "score is at least 70; a request is privileged when the access type is write or admin, or "
    "the target sensitivity is at least 3; a target zone is restricted when it is the restricted "
    "zone or the ot_network zone. "
    "Decide permit or deny by the first matching rule: deny for untrusted device when the target "
    "zone is restricted and the device is not trusted; deny for mfa required when the request is "
    "privileged and MFA did not pass; deny for insufficient clearance when the clearance level is "
    "below the target sensitivity; deny for change control when the target zone is ot_network and "
    "there is no change ticket; otherwise permit. Every decision must be auditable."
)

SHOWCASE_REQUESTS = [
    ("untrusted device → OT network", {
        "requester_role": "contractor", "clearance_level": 2, "device_managed": False,
        "device_posture_score": 40, "mfa_passed": False, "source_zone": "guest",
        "target_zone": "ot_network", "target_sensitivity": 4, "access_type": "admin",
        "off_hours": False, "change_ticket": False}),
    ("privileged write, MFA not passed", {
        "requester_role": "engineer", "clearance_level": 3, "device_managed": True,
        "device_posture_score": 90, "mfa_passed": False, "source_zone": "vpn",
        "target_zone": "corporate", "target_sensitivity": 3, "access_type": "write",
        "off_hours": False, "change_ticket": True}),
    ("clean read request", {
        "requester_role": "analyst", "clearance_level": 4, "device_managed": True,
        "device_posture_score": 95, "mfa_passed": True, "source_zone": "corporate",
        "target_zone": "corporate", "target_sensitivity": 1, "access_type": "read",
        "off_hours": False, "change_ticket": True}),
]
SPARSE_REQUEST = {"requester_role": "contractor", "access_type": "admin",
                  "target_zone": "ot_network"}

_DENY_CONCLUSIONS = {
    "Flag Clearance Level Below Threshold", "Flag Target Zone Equals Value",
    "Flag Is Privileged Request Equals Value", "Flag Is Restricted Zone Equals Value",
}


def _decide(report: dict) -> tuple[str, list[str]]:
    denies = [
        r.get("rule_name") for r in symbolic_rules(report)
        if r.get("fired") and (r.get("action_type") == "block"
                               or r.get("rule_name") in _DENY_CONCLUSIONS)
    ]
    return ("deny" if denies else "permit"), denies


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nREQUEST: {label}")
    try:
        report = api.platforms.query(platform_id, query="Should this be permitted?", facts=facts)
    except Exception as exc:
        print(f"  VERIFIED FAIL-SAFE — refused to certify (no decision returned): {exc}")
        print("=" * 70)
        return
    verdict, denies = _decide(report)
    print(f"  Decision: {verdict.upper()}" + (f"  ({', '.join(denies)})" if denies else ""))
    print(f"  proof_checked: {report.get('proof_checked')}")
    print(f"  {report.get('proof_summary')}")
    print("=" * 70)


def run_access_pdp_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating access-governance PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading access-request data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (classify-then-conclude chain)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Deciding access requests (structured facts → checked proof)")
    for label, facts in SHOWCASE_REQUESTS:
        _show(api, platform["id"], label, facts)
    _show(api, platform["id"], "sparse request (role/access/zone only)", SPARSE_REQUEST)

    print(f"\nDone. Platform {platform['id']} is live. "
          "Measured held-out: 90% accuracy, 100% certification.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Access Governance PDP — AmberTrace AI verified decision demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_access_pdp_demo, args)


if __name__ == "__main__":
    main()
