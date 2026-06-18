"""24 — Air Track Triage (High-Spec ISR).

A standards-shaped variant of the Air-Track Triage demo (see ``19``). Same
defensive, human-in-the-loop triage — clear / monitor / escalate, where escalate
routes to a human operator — but over a richer **ISR surveillance-track schema**
that resembles the output of an ISR data-assurance / track-fusion layer. The
platform never takes autonomous action: its role is auditable, proof-carrying
decision support with a human in the loop.

Standards mapping (open analogues; unclassified). The schema is modelled on what
a track-fusion product (e.g. a TactiQL / FULCRUM-style ISR layer; no public API,
so this emulates the *output format*, not any platform) would emit:

  position_source, mode3a_code, spi,    ASTERIX Cat 021 / Cat 062 surveillance
  baro/geo altitudes, ground speed,     fields (position source, Mode 3/A + SPI,
  track angle, vertical rate              barometric/geometric altitude, track velocity)
  sensor_platform, sensor_lat/lon,      MISB ST 0601 Tags 13/14/15 (sensor
  sensor_true_altitude_ft, slant_range    lat/lon/true-alt) + Tag 21 (slant range)
  track_confidence                      per-sensor / fusion confidence
  iff_mode, flight_plan_correlated,     NOTIONAL overlays computed locally for an
  in_restricted_zone, corridor_compliant  unclassified demo (no real IFF /
                                          restricted-airspace data)

The triage policy and ground truth are identical to ``19`` — only the schema is
richer. The dataset is **synthetic and reproducible** (seeded; ``data/
air_tracks_hispec.csv``); it carries no real surveillance data and is safe to
redistribute.

  1. Create domain (names the boolean classifications)
  2. Upload features-only standardised track data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Triage tracks from structured facts → checked proof per decision

The uploaded ``air_tracks_hispec.csv`` is **features only** — uploading the
ground-truth ``decision`` column would make the build learn a trivial label
classifier instead of the policy chain. A verified query that cannot be certified
is fail-closed refused (HTTP 503); the showcase reports that and continues rather
than aborting.

Creates resources on your account. Run with --help for options.

    python 24_air_track_isr_hispec.py
    python 24_air_track_isr_hispec.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "air_tracks_hispec.csv"

DOMAIN_NAME = "Air Track Triage (High-Spec ISR)"
DOMAIN_DESCRIPTION = (
    "Air-track identification and triage decision support that ingests standardised "
    "ISR surveillance tracks for a recognized air picture. Each track has a position "
    "source (ads_b, asterix_radar, mlat, flarm, or fused), a Mode 3/A code, an "
    "emergency-squawk flag, a special-position-indicator flag, an IFF/SIF mode "
    "(mode3_valid, mode3_invalid, no_response, or emergency), whether it correlates to "
    "a filed flight plan, whether it is on the ground, a barometric altitude in feet, a "
    "geometric altitude in feet, a ground speed in knots, a track angle in degrees, a "
    "vertical rate in feet per minute, a latitude and longitude, whether it is inside a "
    "restricted operating zone, whether it is corridor-compliant, whether its origin is "
    "known, the observing sensor platform with its latitude, longitude and true "
    "altitude, the slant range in metres, and a track confidence. "
    "Classify these named conditions: a track is an emergency when its emergency-squawk "
    "flag is set or its IFF mode is emergency; a track is identified when it correlates "
    "to a filed flight plan and its IFF mode is mode3_valid; a track is a zone breach "
    "when it is inside a restricted operating zone and is not corridor-compliant; a "
    "track is kinematically implausible when its ground speed is at least 600 knots and "
    "its barometric altitude is at most 2000 feet, or its vertical rate is at least 8000 "
    "feet per minute. "
    "Triage each track by the first matching rule: escalate to an operator for an "
    "emergency track; escalate for a zone breach; escalate for an unidentified track "
    "when it is not identified and its IFF mode is no_response or mode3_invalid; monitor "
    "a kinematically implausible track; monitor an unidentified track otherwise; clear "
    "the track when none of the above apply. Every triage decision must be auditable, "
    "and emergency tracks must always be escalated to a human operator and never "
    "suppressed."
)

# A standardised track is many fields; start from a clean baseline and override.
_BASE_TRACK = {
    "track_number": 1, "icao24": "3c5eec", "callsign": "DLH4AB", "origin_country": "Germany",
    "position_source": "ads_b", "mode3a_code": "1000", "emergency_squawk": False, "spi": False,
    "iff_mode": "mode3_valid", "flight_plan_correlated": True, "on_ground": False,
    "baro_altitude_ft": 34000, "geo_altitude_ft": 34250, "ground_speed_kts": 440,
    "track_angle_deg": 95, "vertical_rate_fpm": 0, "latitude_deg": 47.30, "longitude_deg": 8.40,
    "in_restricted_zone": False, "corridor_compliant": True, "origin_known": True,
    "sensor_platform": "GS-RADAR-02", "sensor_latitude": 47.50, "sensor_longitude": 9.00,
    "sensor_true_altitude_ft": 1500, "slant_range_m": 62000, "track_confidence": 0.90,
}


def _track(**overrides) -> dict:
    t = dict(_BASE_TRACK)
    t.update(overrides)
    return t


# Showcase tracks mirroring a drone-surge scenario: dense civil traffic, multi-source,
# mixed confidence, near a restricted energy-facility zone. (label, expected, facts)
SHOWCASE_TRACKS = [
    ("emergency squawk 7700 near the energy facility, also fast-low — safety escalation wins",
     "escalate", _track(
         position_source="fused", mode3a_code="7700", emergency_squawk=True,
         iff_mode="emergency", flight_plan_correlated=False, in_restricted_zone=True,
         corridor_compliant=False, baro_altitude_ft=1200, ground_speed_kts=640,
         latitude_deg=47.00, longitude_deg=8.00, track_confidence=0.93, origin_known=False)),
    ("uncoordinated detection, no IFF/no callsign, in restricted zone off-corridor — escalate",
     "escalate", _track(
         position_source="asterix_radar", callsign="UNKNOWN", mode3a_code="",
         iff_mode="no_response", flight_plan_correlated=False, in_restricted_zone=True,
         corridor_compliant=False, baro_altitude_ft=2400, ground_speed_kts=110,
         latitude_deg=47.01, longitude_deg=8.01, origin_known=False, track_confidence=0.62)),
    ("valid Mode-S airliner inside the zone but corridor-compliant — clears",
     "clear", _track(
         in_restricted_zone=True, corridor_compliant=True, baro_altitude_ft=9000,
         ground_speed_kts=300, latitude_deg=47.00, longitude_deg=8.02, track_confidence=0.95)),
    ("valid IFF but no filed flight-plan correlation — identification incomplete, monitor",
     "monitor", _track(
         position_source="ads_b", iff_mode="mode3_valid", flight_plan_correlated=False,
         callsign="N512TQ", origin_known=False, track_confidence=0.88)),
    ("fast-low track at 650 kts / 1500 ft — kinematically implausible, monitor",
     "monitor", _track(
         position_source="mlat", iff_mode="mode3_valid", flight_plan_correlated=False,
         ground_speed_kts=650, baro_altitude_ft=1500, track_confidence=0.58)),
]

def _show(api, platform_id: int, label: str, facts: dict, expected: str | None) -> None:
    print(f"\n{'=' * 70}\nTRACK: {label}")
    print(f"  source={facts['position_source']} iff={facts['iff_mode']} "
          f"zone={facts['in_restricted_zone']} corridor_ok={facts['corridor_compliant']} "
          f"conf={facts['track_confidence']}")
    try:
        report = api.platforms.query(platform_id, query="Triage this track.", facts=facts)
    except AmbertraceError as exc:
        print(f"  Triage: UNCERTIFIED — query fail-closed ({exc})"
              + (f"   [!! expected {expected}]" if expected else ""))
        print("=" * 70)
        return
    level = report.get("decision", "clear")
    mark = "" if expected is None else (
        "   [OK]" if level == expected else f"   [!! expected {expected}]")
    print(f"  Triage: {level.upper()}{mark}")
    print(f"  proof_checked: {report.get('proof_checked')}")
    answer = (report.get("answer") or "").strip().replace("\n", " ")
    if answer:
        print(f"  Answer: {answer[:160]}")
    print("=" * 70)


def run_air_track_hispec_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/air_tracks_hispec.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating high-spec air-track triage domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading standardised track data (features only)")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (classify-then-conclude chain)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=14)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Triaging standardised tracks (facts → checked proof)")
    for label, expected, facts in SHOWCASE_TRACKS:
        _show(api, platform["id"], label, facts, expected)

    print(f"\nDone. Platform {platform['id']} is live. Standardised ISR schema "
          "(ASTERIX Cat 021/062 + MISB ST 0601 + per-track sensor confidence), "
          "synthetic data.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="High-Spec Air-Track Triage — AmberTrace AI verified C2 decision support demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_air_track_hispec_demo, args)


if __name__ == "__main__":
    main()
