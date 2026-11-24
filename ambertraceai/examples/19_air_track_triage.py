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
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "air_tracks.csv"

DOMAIN_NAME = "Air Track Triage"
DOMAIN_DESCRIPTION = (
    "Decide how to triage each air track for a recognized air picture: escalate, monitor, or clear. "
    "Each track has sensor_source, iff_mode (mode3_valid, mode3_invalid, no_response, or emergency), "
    "squawk_emergency, flight_plan_correlated, transponder_active, in_restricted_zone, corridor_compliant, "
    "altitude_ft, speed_kts, climb_rate_fpm, and origin_known. "
    "A track is an emergency when squawk_emergency is set or iff_mode is emergency. "
    "A track is a zone breach when in_restricted_zone is set and corridor_compliant is not. "
    "A track is kinematically implausible when speed_kts is at least 600 and altitude_ft is at most 2000, "
    "or climb_rate_fpm is at least 8000. "
    "If the track is an emergency, escalate: an emergency track must always be escalated to a human operator "
    "and never suppressed. "
    "If it is a zone breach, escalate. "
    "If iff_mode is no_response or mode3_invalid, escalate. "
    "If it is kinematically implausible, monitor. "
    "If flight_plan_correlated is not set or iff_mode is not mode3_valid, monitor. "
    "Otherwise, clear. Every triage decision must be auditable."
)

# The Decision Table: the outcomes a triage decision can take, declared (not guessed from
# the description's verbs). `label` is served verbatim in `decision`; higher `order` wins when
# several fire; `default` is the outcome when nothing fires; `permits` says whether the action
# may proceed. Declared at create => applied "confirmed". Read it back on
# platforms.status(id)["decision_table"].
DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "escalate", "order": 3, "permits": False},
        {"label": "monitor", "order": 2, "permits": False},
        {"label": "clear", "order": 1, "default": True, "permits": True},
    ],
}

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


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nTRACK: {label}")
    report = api.platforms.query(platform_id, query="Triage this track.", facts=facts)
    level = report.get("decision", "unknown")
    deciding = (report.get("explanation") or {}).get("decision", {}).get("deciding_rules", [])
    rule_names = [r.get("rule", "") for r in deciding]
    print(f"  Triage: {level.upper()}" + (f"  ({', '.join(rule_names)})" if rule_names else ""))
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
    domain = api.domains.create(
        name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION,
        decision_table=DECISION_TABLE)
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
        # The domain's table plants a default outcome: declare it (the platform default is fail-closed, see 72).
        decision_posture="default_allow",
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
