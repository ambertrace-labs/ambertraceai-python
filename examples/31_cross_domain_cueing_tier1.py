"""Cross-Domain Cueing, Tier 1 — the JOIN brought INSIDE the proof.

Tier 0 (``25_cross_domain_cueing.py``) proves a fused-track triage decision *given*
two caller-pre-joined cue booleans (`grid_has_confirmed_maritime_exclusion_breach`,
`grid_has_gps_spoofing`). The honest claim there is only *conditional* on those
booleans — the platform doesn't certify that the cue was correctly derived from the
underlying maritime / cyber tracks.

**Tier 1 removes the pre-joined booleans and derives the cue INSIDE the proof.** The
domain declares two certified RELATIONS — ``maritime_track`` and ``cyber_event`` —
and the description states the cue as an EXISTENTIAL over them:

    "a track is maritime-cued when there EXISTS a related maritime_track in the same
     grid_square whose zone_status is exclusion_breach and ais_corroborated is true"

The builder authors an ``existsRelated`` derive rule for that clause. At query time
the caller attaches the related rows for the focal track's grid via
``relations={relation_name: [row, ...]}``; the verified kernel folds them — joined on
``grid_square`` — and derives the cue. Every related row is certified per-cell at the
platform's confidence threshold; if any is rejected the query fails CLOSED. When a cue
fires, the matched related rows are surfaced in ``explanation.relation_provenance`` —
so the escalation is auditable back to the exact maritime/cyber records that caused it.

  1. Generate synthetic fused tracks:  python gen_fused_tracks.py
  2. Create the domain (declares the two relations in its description)
  3. Upload FOCAL-ONLY data (the two cue booleans dropped) + build the ontology
     WITH ``relations=`` (the builder authors the existsRelated cue rules)
  4. Build a verified platform (tau = 0.6)
  5. Triage tracks from focal facts + attached related rows -> checked proof + provenance

Runs against https://app.ambertrace.ai via the published ``ambertraceai`` SDK.
Synthetic data; the reference policy lives in ``gen_fused_tracks.reference_policy``.
"""

from __future__ import annotations

import argparse
import csv
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
DEFAULT_DATASET = DATA_DIR / "fused_tracks.csv"
DEFAULT_HOLDOUT = DATA_DIR / "fused_tracks_holdout.csv"

QUERY_TEXT = "Triage this track."

# The two cue booleans are DROPPED from the focal row — in Tier 1 they are derived
# in-proof from the attached relations, not supplied.
_CUE_COLS = ("grid_has_confirmed_maritime_exclusion_breach", "grid_has_gps_spoofing")

DOMAIN_NAME = "Cross-Domain Cueing (Tier 1 — existential join in-proof)"
DOMAIN_DESCRIPTION = (
    "Multi-domain track triage for cross-domain cueing. Each track has a domain (air or "
    "maritime), a grid square, a position source (gps, radar, ais, or sonar), an identification "
    "(unidentified, friendly, hostile, or unknown), whether it is inside an exclusion zone, and a "
    "track confidence between 0 and 1. "
    "There are related maritime_track records, each with a grid square, a zone status, and whether "
    "it is ais_corroborated; and related cyber_event records, each with a grid square and an "
    "event type. "
    "Classify these named conditions: a track is unidentified when its identification is "
    "unidentified; a track is hostile when its identification is hostile; a track is maritime-cued "
    "when there exists a related maritime_track in the same grid_square whose zone_status is "
    "exclusion_breach and ais_corroborated is true; a track is grid-spoofed when there exists a "
    "related cyber_event in the same grid_square whose event_type is gps_spoofing; a track is "
    "position-untrusted when it is grid-spoofed and its position source is gps; a track is a "
    "cross-domain threat when it is maritime-cued and unidentified; a track is a zone intrusion "
    "when it is inside an exclusion zone and unidentified; a track is a confident unknown when it "
    "is unidentified and its track confidence is at least 0.6; a track is zone-resident when it is "
    "inside an exclusion zone. "
    "Triage each track by the first matching rule: escalate a cross-domain threat track; escalate "
    "a zone intrusion track; escalate a hostile track; monitor a confident unknown track; monitor "
    "a zone-resident track; monitor a position-untrusted track; clear the track when none of the "
    "above apply."
)

# The certified relation schemas (Tier-1). Declared at build time so the
# existsRelated cue rules ground against them; rows are attached per query.
RELATIONS = [
    {"name": "maritime_track", "join_key": "grid_square", "columns": [
        {"name": "grid_square", "type": "string"},
        {"name": "zone_status", "type": "enum",
         "enum_values": ["normal", "loitering", "exclusion_breach"]},
        {"name": "ais_corroborated", "type": "bool"}]},
    {"name": "cyber_event", "join_key": "grid_square", "columns": [
        {"name": "grid_square", "type": "string"},
        {"name": "event_type", "type": "enum",
         "enum_values": ["gps_spoofing", "jamming", "normal"]},
        {"name": "confidence", "type": "float"}]},
]

_BASE_TRACK = {
    "domain": "air", "grid_square": "GS-22", "position_source": "radar",
    "identification": "unidentified", "in_exclusion_zone": False, "track_confidence": 0.70,
}


def _clear_grid(grid: str) -> dict:
    """Related rows for a grid with NO breach and NO spoofing (the cue is absent)."""
    return {
        "maritime_track": [{"grid_square": grid, "zone_status": "normal", "ais_corroborated": True}],
        "cyber_event": [{"grid_square": grid, "event_type": "normal", "confidence": 0.9}],
    }


def _breach_grid(grid: str) -> dict:
    """Related rows for a grid WITH a corroborated maritime exclusion breach."""
    rel = _clear_grid(grid)
    rel["maritime_track"] = [
        {"grid_square": grid, "zone_status": "exclusion_breach", "ais_corroborated": True}]
    return rel


def _spoofed_grid(grid: str) -> dict:
    """Related rows for a grid WITH a GPS-spoofing cyber event."""
    rel = _clear_grid(grid)
    rel["cyber_event"] = [{"grid_square": grid, "event_type": "gps_spoofing", "confidence": 0.9}]
    return rel


# Each showcase pair proves a cross-cue derived IN-PROOF: same focal track, the cue
# established purely by the ATTACHED related rows. (label, expected, focal, relations)
SHOWCASE = [
    ("low-confidence unidentified air track, clear grid — monitors on its own",
     "monitor", dict(_BASE_TRACK, grid_square="GS-22"), _clear_grid("GS-22")),
    ("SAME track — now an exclusion_breach maritime_track exists in its grid: the "
     "existsRelated cue derives maritime-cued -> cross-domain threat -> ESCALATE",
     "escalate", dict(_BASE_TRACK, grid_square="GS-22"), _breach_grid("GS-22")),
    ("GPS-sourced track in a grid with a gps_spoofing cyber_event — position-untrusted -> MONITOR",
     "monitor", dict(_BASE_TRACK, grid_square="GS-13", position_source="gps",
                     identification="friendly", track_confidence=0.9), _spoofed_grid("GS-13")),
    ("radar-sourced track in the SAME spoofed grid — position trusted -> CLEARS",
     "clear", dict(_BASE_TRACK, grid_square="GS-13", position_source="radar",
                   identification="friendly", track_confidence=0.9), _spoofed_grid("GS-13")),
]


def _write_focal_only(src: Path, dst: Path) -> list[str]:
    """Write a focal-only copy of the training CSV with the cue booleans dropped."""
    rows = list(csv.DictReader(open(src, newline="")))
    cols = [c for c in rows[0].keys() if c not in _CUE_COLS and c != "track_id"]
    with open(dst, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow({c: r[c] for c in cols})
    return cols


def _show(api, platform_id: int, label: str, facts: dict, relations: dict,
          expected: str | None = None) -> bool:
    print(f"\n{'=' * 70}\nTRACK: {label}")
    report = api.platforms.query(platform_id, query=QUERY_TEXT, facts=facts, relations=relations)
    level = report.get("decision")
    ok = expected is None or level == expected
    mark = "" if expected is None else ("   [OK]" if ok else f"   [!! expected {expected}]")
    print(f"  Triage: {str(level).upper()}{mark}")
    print(f"  proof_checked: {report.get('proof_checked')}")
    prov = (report.get("explanation") or {}).get("relation_provenance")
    if prov:
        for head, p in prov.items():
            ids = [r.get("grid_square") for r in p.get("matched", [])]
            print(f"  cue {head}: derived from {p.get('relation')} rows in {ids} "
                  f"(count {p.get('count')})")
    print("=" * 70)
    return ok


def _per_row_relations(row: dict) -> dict:
    """Build the attached relations for a holdout row from its cue booleans."""
    grid = row["grid_square"]
    breach = int(row["grid_has_confirmed_maritime_exclusion_breach"]) == 1
    spoof = int(row["grid_has_gps_spoofing"]) == 1
    return {
        "maritime_track": [{"grid_square": grid,
                            "zone_status": "exclusion_breach" if breach else "normal",
                            "ais_corroborated": True}],
        "cyber_event": [{"grid_square": grid,
                         "event_type": "gps_spoofing" if spoof else "normal",
                         "confidence": 0.9}],
    }


def _score_holdout(api, platform_id: int, holdout: Path) -> None:
    rows = list(csv.DictReader(open(holdout, newline="")))
    n = len(rows)
    correct = certified = query_failed = over_permit = prov_on_cued = 0
    for row in rows:
        truth = row["decision"]
        facts = {"domain": row["domain"], "grid_square": row["grid_square"],
                 "position_source": row["position_source"], "identification": row["identification"],
                 "in_exclusion_zone": bool(int(row["in_exclusion_zone"])),
                 "track_confidence": float(row["track_confidence"])}
        relations = _per_row_relations(row)
        try:
            report = api.platforms.query(platform_id, query=QUERY_TEXT, facts=facts, relations=relations)
        except AmbertraceError:
            query_failed += 1
            continue
        if report.get("proof_checked"):
            certified += 1
        decision = report.get("decision")
        if decision == truth:
            correct += 1
        elif truth == "escalate" and decision == "clear":
            over_permit += 1
        cued = (int(row["grid_has_confirmed_maritime_exclusion_breach"]) == 1
                or (int(row["grid_has_gps_spoofing"]) == 1 and row["position_source"] == "gps"))
        if cued and (report.get("explanation") or {}).get("relation_provenance"):
            prov_on_cued += 1
    acc = (correct / n * 100) if n else 0.0
    print(f"\n  Holdout: {correct}/{n} correct ({acc:.0f}%)  cert={certified}/{n}  "
          f"query_failed={query_failed}  over_permit={over_permit}  provenance_on_cued={prov_on_cued}")
    print(f"  Targets: >= 98% accuracy, cert {n}/{n}, 0 over-permit "
          f"-> {'PASS' if (acc >= 98 and certified == n and over_permit == 0) else 'CHECK'}")


def run_tier1_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Generate it with "
              f"`python gen_fused_tracks.py`.", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating the Tier-1 domain (declares maritime_track + cyber_event relations)")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading FOCAL-ONLY data (cue booleans dropped)")
    focal = args.dataset.with_name("fused_tracks_focal.csv")
    cols = _write_focal_only(args.dataset, focal)
    print(f"  focal columns: {cols}")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(focal))
    print_dataset(dataset)

    print_section(3, total, "Building ontology WITH relations= (authors the existsRelated cue rules)")
    domain = build_ontology(api, domain["id"], relations=RELATIONS)
    print_ontology(domain, limit=16)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Triaging tracks — cue derived in-proof from attached relations")
    showcase_ok = all(
        _show(api, platform["id"], label, facts, relations, expected)
        for label, expected, facts, relations in SHOWCASE)
    print(f"\n  Showcase (cue derived in-proof): {'ALL OK' if showcase_ok else 'MISMATCH — see above'}")
    if not args.no_holdout:
        _score_holdout(api, platform["id"], args.holdout)

    print(f"\nDone. Platform {platform['id']} is live. Tier-1: the maritime/cyber cue is derived "
          "INSIDE the proof by an existsRelated fold over the attached certified relations, joined "
          "on grid_square — with join provenance in explanation.relation_provenance. Synthetic data.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-Domain Cueing Tier 1 — verified existential join in-proof")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--holdout", type=Path, default=DEFAULT_HOLDOUT)
    parser.add_argument("--no-holdout", action="store_true",
                        help="skip the labelled-holdout scoring (showcase rows only)")
    args = parser.parse_args()
    run_demo(run_tier1_demo, args)


if __name__ == "__main__":
    main()
