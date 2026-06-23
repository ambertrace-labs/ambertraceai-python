"""53 — Production Drift Monitoring.

Once a verified platform is approved and serving traffic, you want to know if its
behaviour starts to DRIFT — if the mix of decisions it certifies shifts away from
what it looked like at approval time. This demo walks the monitoring lifecycle on
a verified access-governance platform:

  1. Create the access-governance domain (names the boolean classifications)
  2. Upload access-request data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Capture a DRIFT BASELINE at approval time (the reference behaviour)
  5. Replay a batch of post-deployment requests (simulated operational traffic)
  6. Check for drift against the baseline and report any alerts

`capture_drift_baseline` records the platform's certified behaviour (e.g. its
certified-rejection rate over a sample) at the moment you approve it.
`check_drift` later compares live behaviour to that baseline and returns
`drift_detected` plus any per-signal alerts — the cue for an operator to
re-review or re-build the platform. Drift monitoring is most meaningful on the
verified profile, where the certified-rejection rate is a stable, proof-backed
signal; pass --standard to build a standard platform instead.

Creates resources on your account. Run with --help for options.

    python 53_drift_monitoring.py
    python 53_drift_monitoring.py --standard   # skip verified profile
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
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "access_requests.csv"

DOMAIN_NAME = "Access Governance — Drift Monitoring"
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

# A batch of post-deployment requests standing in for live operational traffic.
# In production these would be the real requests the PDP has served since the
# baseline was captured; here they are a fixed, reproducible sample.
LIVE_TRAFFIC = [
    {"requester_role": "contractor", "clearance_level": 2, "device_managed": False,
     "device_posture_score": 40, "mfa_passed": False, "source_zone": "guest",
     "target_zone": "ot_network", "target_sensitivity": 4, "access_type": "admin",
     "off_hours": True, "change_ticket": False},
    {"requester_role": "engineer", "clearance_level": 3, "device_managed": True,
     "device_posture_score": 90, "mfa_passed": False, "source_zone": "vpn",
     "target_zone": "corporate", "target_sensitivity": 3, "access_type": "write",
     "off_hours": False, "change_ticket": True},
    {"requester_role": "analyst", "clearance_level": 4, "device_managed": True,
     "device_posture_score": 95, "mfa_passed": True, "source_zone": "corporate",
     "target_zone": "corporate", "target_sensitivity": 1, "access_type": "read",
     "off_hours": False, "change_ticket": True},
    {"requester_role": "contractor", "clearance_level": 1, "device_managed": False,
     "device_posture_score": 30, "mfa_passed": False, "source_zone": "guest",
     "target_zone": "restricted", "target_sensitivity": 4, "access_type": "admin",
     "off_hours": True, "change_ticket": False},
]


def _print_baseline(baseline: dict) -> None:
    print(f"  Certified-rejection rate: {baseline.get('certified_rejection_rate', 'n/a')}")
    print(f"  Baseline samples (n):     {baseline.get('n', 0)}")


def _replay_traffic(api, platform_id: int) -> None:
    served = fail_closed = 0
    for i, facts in enumerate(LIVE_TRAFFIC, start=1):
        try:
            report = api.platforms.query(
                platform_id, query="Should this access be permitted?", facts=facts)
            served += 1
            print(f"    request {i}: served (proof_checked={report.get('proof_checked')})")
        except AmbertraceError as exc:
            if getattr(exc, "status_code", None) == 503 or \
                    getattr(exc, "code", "") == "service_unavailable":
                fail_closed += 1
                print(f"    request {i}: fail-closed (could not certify)")
            else:
                raise
    print(f"  Replayed {len(LIVE_TRAFFIC)} requests: {served} served, "
          f"{fail_closed} fail-closed.")


def run_drift_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 6

    print_section(1, total, "Creating access-governance domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading access-request data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building verified platform")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(4, total, "Capturing the drift baseline (approval time)")
    print("  The baseline records the platform's certified behaviour at approval,\n"
          "  so later traffic can be compared against it.")
    try:
        baseline = api.platforms.capture_drift_baseline(platform["id"])
        _print_baseline(baseline)
    except AmbertraceError as exc:
        print(f"  capture_drift_baseline unavailable "
              f"({getattr(exc, 'status_code', '?')} {getattr(exc, 'code', '?')}): {exc}")

    print_section(5, total, "Replaying post-deployment traffic (simulated)")
    _replay_traffic(api, platform["id"])

    print_section(6, total, "Checking for drift against the baseline")
    try:
        drift = api.platforms.check_drift(platform["id"])
        detected = drift.get("drift_detected", False)
        print(f"  drift_detected: {detected}")
        alerts = drift.get("alerts", [])
        if alerts:
            for alert in alerts:
                print(f"    ALERT: {alert.get('signal')} — {alert.get('message', '')}")
        else:
            print("    No drift alerts — live behaviour matches the approval baseline.")
        if detected:
            print("\n  Operator action: a detected drift is the cue to re-review the\n"
                  "  platform's rules or re-build it on fresh data before trusting new decisions.")
    except AmbertraceError as exc:
        print(f"  check_drift unavailable "
              f"({getattr(exc, 'status_code', '?')} {getattr(exc, 'code', '?')}): {exc}")

    print(f"\nDone. Platform {platform['id']} is live. "
          "Re-run check_drift on a schedule to monitor behaviour over time.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Production Drift Monitoring — AmberTrace AI verified-platform "
                    "behavioural drift demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_drift_demo, args)


if __name__ == "__main__":
    main()
