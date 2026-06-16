"""50 — Verified vs Standard.

Same access-governance data, two platforms built side by side: a STANDARD
platform that answers from neural retrieval, and a VERIFIED platform that
returns proof-carrying decisions or fail-closes (HTTP 503) when it cannot
certify. The contrast is the point — on an under-specified request the standard
platform still produces an answer, while the verified platform refuses.

  1. Create access-governance domain + upload data + build ontology
  2. Build a standard (non-verified) platform
  3. Build a verified platform (τ = 0.6)
  4. Define a complete deny-worthy request and a sparse, under-specified one
  5. Query BOTH platforms with the same facts and print them side by side

Creates resources on your account. Run with --help for options.

    python 50_verified_vs_standard.py
    python 50_verified_vs_standard.py --tau 0.7 -v
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ambertraceai import AmbertraceError

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

DOMAIN_NAME = "Access Governance PDP (verified vs standard)"
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

_DENY_CONCLUSIONS = {
    "Flag Clearance Level Below Threshold", "Flag Target Zone Equals Value",
    "Flag Is Privileged Request Equals Value", "Flag Is Restricted Zone Equals Value",
}

# (a) A COMPLETE, clearly deny-worthy request: untrusted device → ot_network.
COMPLETE_REQUEST = {
    "requester_role": "contractor", "clearance_level": 2, "device_managed": False,
    "device_posture_score": 40, "mfa_passed": False, "source_zone": "guest",
    "target_zone": "ot_network", "target_sensitivity": 4, "access_type": "admin",
    "off_hours": False, "change_ticket": False,
}
# (b) A SPARSE, under-specified request: not enough to certify a decision.
SPARSE_REQUEST = {
    "requester_role": "contractor", "access_type": "admin", "target_zone": "ot_network",
}


def _decide(report: dict) -> tuple[str, list[str]]:
    """Decode permit/deny from the certified symbolic trace (cf. demo 18)."""
    denies = [
        r.get("rule_name") for r in symbolic_rules(report)
        if r.get("fired") and (r.get("action_type") == "block"
                               or r.get("rule_name") in _DENY_CONCLUSIONS)
    ]
    return ("deny" if denies else "permit"), denies


def _is_fail_closed(exc: AmbertraceError) -> bool:
    return getattr(exc, "status_code", None) == 503 or \
        getattr(exc, "code", "") == "service_unavailable"


def _query_both(api, standard_id: int, verified_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nREQUEST: {label}")
    print(f"  facts: {facts}")

    # Standard platform — neural retrieval; answers even when under-specified.
    print("\n  STANDARD platform:")
    try:
        std = api.platforms.query(standard_id, query="Should this be permitted?", facts=facts)
        answer = (std.get("answer") or "")[:160]
        print(f"    answer:        {answer}")
        print(f"    proof_checked: {std.get('proof_checked')}")
    except AmbertraceError as exc:
        print(f"    ERROR: {exc}")

    # Verified platform — proof-carrying decision, or fail-closed refusal.
    print("\n  VERIFIED platform:")
    try:
        ver = api.platforms.query(verified_id, query="Should this be permitted?", facts=facts)
    except AmbertraceError as exc:
        if _is_fail_closed(exc):
            print("    VERIFIED FAIL-CLOSED — refused to certify "
                  f"(no decision returned). ({exc})")
            print("=" * 70)
            return
        raise
    verdict, denies = _decide(ver)
    print(f"    decision:      {verdict.upper()}" + (f"  ({', '.join(denies)})" if denies else ""))
    print(f"    proof_checked: {ver.get('proof_checked')}")
    if ver.get("proof_summary"):
        print(f"    proof_summary: {ver.get('proof_summary')}")
    print("=" * 70)


def run_verified_vs_standard_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating access-governance PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(2, total, "Building standard (non-verified) platform")
    standard = build_platform(api, domain["id"], dataset["id"], verified_profile=False)
    print(f"  Platform {standard['id']}: {standard['name']} ({standard.get('status')}, standard)")

    print_section(3, total, "Building verified platform")
    verified = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=True, verified_min_confidence=args.tau,
    )
    print(f"  Platform {verified['id']}: {verified['name']} ({verified.get('status')}, verified)")

    print_section(4, total, "Showcase inputs (complete vs sparse)")
    print("  (a) complete deny-worthy request: untrusted device → ot_network")
    print("  (b) sparse request: role + access_type + target_zone only")

    print_section(5, total, "Querying both platforms (same facts, side by side)")
    _query_both(api, standard["id"], verified["id"],
                "complete — untrusted device → OT network", COMPLETE_REQUEST)
    _query_both(api, standard["id"], verified["id"],
                "sparse — role/access/zone only", SPARSE_REQUEST)

    print("\n  The sparse request is the point: standard produces an answer; verified")
    print("  refuses to certify and fail-closes. Verified never guesses.")
    print(f"\nDone. Standard platform {standard['id']} and verified platform "
          f"{verified['id']} are live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verified vs Standard — AmberTrace AI fail-closed demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_verified_vs_standard_demo, args)


if __name__ == "__main__":
    main()
