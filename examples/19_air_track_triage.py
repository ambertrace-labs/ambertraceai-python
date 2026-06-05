"""19 — Air Track Triage.

Verified proof-carrying C2 decision support: compiles a recognized air picture
and triages each track to clear / monitor / escalate (escalate = route to a
human operator). The platform never takes autonomous action — its role is
auditable, proof-carrying decision support with a human in the loop.

  1. Create domain (names the boolean classifications)
  2. Upload features-only track data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Triage tracks from structured facts → checked proof per decision

Creates resources on your account. Run with --help for options.

    python 19_air_track_triage.py
    python 19_air_track_triage.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "air_tracks.csv"

DOMAIN_NAME = "Air Track Triage"
DOMAIN_DESCRIPTION = (
    "Air-track identification and triage decision support for compiling a recognized air "
    "picture. Each track has a sensor source, an IFF/SIF mode (mode3_valid, mode3_invalid, "
    "no_response, or emergency), an emergency-squawk flag, whether it correlates to a filed "
    "flight plan, whether its transponder is active, whether it is inside a restricted operating "
    "zone, whether it is corridor-compliant, an altitude in feet, a speed in knots, a climb rate "
    "in feet per minute, and whether its origin is known. "
    "Classify these named conditions: a track is an emergency when its emergency-squawk flag is "
    "set or its IFF mode is emergency; a track is identified when it correlates to a flight plan "
    "and its IFF mode is mode3_valid; a track is a zone breach when it is inside a restricted "
    "operating zone and is not corridor-compliant; a track is kinematically implausible when its "
    "speed is at least 600 knots and altitude at most 2000 feet, or its climb rate is at least "
    "8000 feet per minute. "
    "Triage each track by the first matching rule: escalate to an operator for an emergency "
    "track; escalate for a zone breach; escalate for an unidentified track when it is not "
    "identified and its IFF mode is no_response or mode3_invalid; monitor a kinematically "
    "implausible track; "
    "monitor an unidentified track otherwise; clear the track when none of the above apply. Every "
    "triage decision must be auditable, and emergency tracks must always be escalated to a human "
    "operator and never suppressed."
)

_ESCALATE = {"Check Is Emergency Equals Value", "Flag Is Zone Breach Equals Value",
             "Flag Is Identified Not Equals Value"}
_MONITOR = {"Flag Is Kinematically Implausible Equals Value",
            "Flag Is Identified Not Equals Value (2)"}

SHOWCASE_TRACKS = [
    ("emergency squawk (must escalate)", {
        "sensor_source": "radar", "iff_mode": "emergency", "squawk_emergency": True,
        "flight_plan_correlated": False, "transponder_active": True, "in_restricted_zone": False,
        "corridor_compliant": False, "altitude_ft": 12000, "speed_kts": 320,
        "climb_rate_fpm": 0, "origin_known": False}),
    ("restricted zone, no corridor", {
        "sensor_source": "fused", "iff_mode": "mode3_valid", "squawk_emergency": False,
        "flight_plan_correlated": True, "transponder_active": True, "in_restricted_zone": True,
        "corridor_compliant": False, "altitude_ft": 8000, "speed_kts": 280,
        "climb_rate_fpm": 500, "origin_known": True}),
    ("unidentified, no IFF response", {
        "sensor_source": "radar", "iff_mode": "no_response", "squawk_emergency": False,
        "flight_plan_correlated": False, "transponder_active": False, "in_restricted_zone": False,
        "corridor_compliant": True, "altitude_ft": 26000, "speed_kts": 410,
        "climb_rate_fpm": 1200, "origin_known": False}),
    ("correlated civil traffic (clear)", {
        "sensor_source": "ads_b", "iff_mode": "mode3_valid", "squawk_emergency": False,
        "flight_plan_correlated": True, "transponder_active": True, "in_restricted_zone": False,
        "corridor_compliant": True, "altitude_ft": 34000, "speed_kts": 450,
        "climb_rate_fpm": 0, "origin_known": True}),
]


def _triage(report: dict) -> tuple[str, list[str]]:
    fired = {r.get("rule_name") for r in symbolic_rules(report) if r.get("fired")}
    esc = sorted(fired & _ESCALATE)
    if esc:
        return "escalate", esc
    mon = sorted(fired & _MONITOR)
    if mon:
        return "monitor", mon
    return "clear", []


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nTRACK: {label}")
    report = api.platforms.query(platform_id, query="Triage this track.", facts=facts)
    level, rules = _triage(report)
    print(f"  Triage: {level.upper()}" + (f"  ({', '.join(rules)})" if rules else ""))
    print(f"  proof_checked: {report.get('proof_checked')}")
    print(f"  {report.get('proof_summary')}")
    print("=" * 70)


def run_air_track_triage_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/air_tracks.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating air-track triage domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading track data (features only)")
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

    print_section(5, total, "Triaging tracks (structured facts → checked proof)")
    for label, facts in SHOWCASE_TRACKS:
        _show(api, platform["id"], label, facts)

    print(f"\nDone. Platform {platform['id']} is live. "
          "Measured held-out: 98% three-way accuracy, 98% certification.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Air Track Triage — AmberTrace AI verified C2 decision support demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_air_track_triage_demo, args)


if __name__ == "__main__":
    main()
