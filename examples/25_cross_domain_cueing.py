"""25 — Cross-Domain Cueing (Tier 0, multi-domain fusion triage).

A single verified core triages BOTH air and maritime-surface tracks that an
upstream fusion / correlation layer has flattened onto one unified ``fused_track``
schema (a ``domain`` discriminator carries air | maritime). Each track is triaged
to clear / monitor / escalate by a first-match ladder with a **top-precedence
cross-domain-cue rule** — escalate regardless of the track's own score when a
confirmed maritime exclusion breach is present in its grid square and the track is
unidentified. Separately, a soft obligation raises ``requires_human_review`` and a
derived ``position_trusted=false`` flag exclude a GPS-spoofed sensor's position
from the decision (the decision is *modelled*, the input is never mutated).

THE HONEST CLAIM (read this). The two cross-domain cue booleans —
``grid_has_confirmed_maritime_exclusion_breach`` (from a maritime domain) and
``grid_has_gps_spoofing`` (from a cyber/EM domain) — enter the verified core as
ordinary **declared inputs, pre-joined by the fusion layer OUTSIDE the proof**.
So the certified claim is *conditional*: every cross-cued escalation is provably
correct GIVEN the caller-derived cue, the precedence override is guaranteed, and
the spoofed sensor is provably excluded from the decision. AmberTrace does NOT (in
Tier 0) join across the other domains' tables at decision time — soundness depends
on a closed fact set per query. Tier 1 (roadmap) brings that correlation *inside*
the proof via a bounded relational rule, so the engine certifies the cue was
correctly derived. This demo is the executable acceptance contract for that work.
See ``../AmbertraceAIUser/docs/design-cross-domain-cueing.md``. Synthetic data,
blue-team framing — no real surveillance data.

  1. Create domain (names the triage ladder + the cross-cue precedence + the
     separate human-review obligation + the position-trust derivation)
  2. Upload features-only fused-track data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Prove the two showcase cross-cues, then score the 50-row labelled holdout

The uploaded ``fused_tracks.csv`` is **features only** — uploading the
ground-truth ``decision`` column would make the build learn a trivial label
classifier instead of the policy chain. The 50-row ``fused_tracks_holdout.csv``
carries the ground-truth label and is scored separately. A verified query that
cannot be certified is fail-closed refused (HTTP 503); the showcase reports that
and continues rather than aborting.

Creates resources on your account. Run with --help for options.

    python 25_cross_domain_cueing.py
    python 25_cross_domain_cueing.py --standard      # skip verified profile
    python 25_cross_domain_cueing.py --no-holdout    # showcase rows only
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

DOMAIN_NAME = "Cross-Domain Cueing (Fused Track Triage)"
# Authored in the access-PDP framing (named conditions + a first-match decision
# ladder + a separate obligation) so the verdict vocabulary is declared — an
# under-declared verdict field defaults to permit-everything. Both operands of
# every cross-field comparison are declared inputs/derived heads (engine landmine:
# an unbound operand defaults open); enums are enumerated positively (no
# ungroundable set-membership / negation heads); the policy is deliberately
# atemporal (no native temporal operator).
DOMAIN_DESCRIPTION = (
    "Cross-domain fusion triage decision support over a unified surveillance track. "
    "An upstream fusion layer correlates air and maritime-surface tracks by grid square "
    "and emits one flattened fused track per query. Each fused track has a domain "
    "(air or maritime), a grid square, a position source (gps, radar, ais, or sonar), an "
    "identification (unidentified, friendly, hostile, or unknown), whether it is in an "
    "exclusion zone, a track confidence between 0 and 1, whether a confirmed maritime "
    "exclusion breach is present in its grid square, and whether GPS spoofing is present "
    "in its grid square. "
    "Classify these named conditions: a track is unidentified when its identification is "
    "unidentified; a track is hostile when its identification is hostile; a track is "
    "cross-cued when a confirmed maritime exclusion breach is present in its grid square "
    "and it is unidentified; a track is a zone breach when it is in an exclusion zone and "
    "is unidentified; a track is confident when its track confidence is at least 0.6; a "
    "track has a spoofed position when GPS spoofing is present in its grid square and its "
    "position source is gps. "
    "Triage each track by the first matching rule: escalate a cross-cued track regardless "
    "of its individual score; escalate a zone-breach track; escalate a hostile track; "
    "monitor an unidentified track that is confident; monitor a track that is in an "
    "exclusion zone; clear the track when none of the above apply. "
    "Separately, require human review when a track has a spoofed position; and when a "
    "track has a spoofed position its position is not trusted, so any escalation that "
    "depends on the reported position must not be certified on position evidence alone. "
    "Every triage decision must be auditable, and a cross-cued track must always be "
    "escalated to a human operator and never suppressed."
)

# A fused track is a handful of fields; start from a clean baseline and override.
_BASE_TRACK = {
    "domain": "air", "grid_square": "GS-22", "position_source": "radar",
    "identification": "friendly", "in_exclusion_zone": False, "track_confidence": 0.90,
    "grid_has_confirmed_maritime_exclusion_breach": False, "grid_has_gps_spoofing": False,
}


def _track(**overrides) -> dict:
    t = dict(_BASE_TRACK)
    t.update(overrides)
    return t


# The two showcase tracks that PROVE the cross-cue (design §5). (label, expected, facts)
#  (a) a low-score unidentified air track that escalates ONLY because of the maritime
#      breach — absent the cue (conf 0.42, not in zone, not hostile) it would CLEAR;
#  (b) a GPS-sourced track flagged for review under spoofing (position not trusted),
#      while a radar-sourced track in the SAME grid under the same spoofing is not.
SHOWCASE_TRACKS = [
    ("(a) low-score unidentified air track — escalates ONLY via the maritime cross-cue",
     "escalate", _track(
         domain="air", grid_square="GS-13", position_source="radar",
         identification="unidentified", in_exclusion_zone=False, track_confidence=0.42,
         grid_has_confirmed_maritime_exclusion_breach=True, grid_has_gps_spoofing=False)),
    ("(b1) GPS-sourced track under grid spoofing — position NOT trusted, review raised",
     "monitor", _track(
         domain="air", grid_square="GS-31", position_source="gps",
         identification="unidentified", in_exclusion_zone=False, track_confidence=0.85,
         grid_has_confirmed_maritime_exclusion_breach=False, grid_has_gps_spoofing=True)),
    ("(b2) radar-sourced track in the SAME spoofed grid — position trusted, no review",
     "monitor", _track(
         domain="air", grid_square="GS-31", position_source="radar",
         identification="unidentified", in_exclusion_zone=False, track_confidence=0.85,
         grid_has_confirmed_maritime_exclusion_breach=False, grid_has_gps_spoofing=True)),
]


def _decision(report: dict) -> str:
    """The authoritative certified verdict. The SDK surfaces it at the top level
    (``report["decision"]``) and under ``explanation.decision.decision`` — read the
    top-level value, falling back to the explanation block."""
    if report.get("decision") is not None:
        return report["decision"]
    decision_block = (report.get("explanation") or {}).get("decision") or {}
    return decision_block.get("decision", "clear")


def _show(api, platform_id: int, label: str, facts: dict, expected: str | None) -> bool:
    print(f"\n{'=' * 70}\nTRACK: {label}")
    print(f"  domain={facts['domain']} grid={facts['grid_square']} "
          f"source={facts['position_source']} id={facts['identification']} "
          f"zone={facts['in_exclusion_zone']} conf={facts['track_confidence']}")
    print(f"  maritime_breach_in_grid={facts['grid_has_confirmed_maritime_exclusion_breach']} "
          f"gps_spoofing_in_grid={facts['grid_has_gps_spoofing']}")
    try:
        report = api.platforms.query(platform_id, query=QUERY_TEXT, facts=facts)
    except AmbertraceError as exc:
        print(f"  Triage: UNCERTIFIED — query fail-closed ({exc})"
              + (f"   [!! expected {expected}]" if expected else ""))
        print("=" * 70)
        return False
    level = _decision(report)
    ok = expected is None or level == expected
    mark = "" if expected is None else ("   [OK]" if ok else f"   [!! expected {expected}]")
    print(f"  Triage: {level.upper()}{mark}")
    print(f"  proof_checked: {report.get('proof_checked')}")
    answer = (report.get("answer") or "").strip().replace("\n", " ")
    if answer:
        print(f"  Answer: {answer[:200]}")
    print("=" * 70)
    return ok


def _coerce(row: dict) -> dict:
    """Type-coerce a holdout CSV row into structured query facts. Label columns are
    dropped; an empty cell is dropped (not asserted) so an out-of-declared-domain
    value fail-closes at query rather than being fabricated."""
    drop = {"track_id", "decision", "requires_human_review", "position_trusted"}
    bool_cols = {"in_exclusion_zone",
                 "grid_has_confirmed_maritime_exclusion_breach", "grid_has_gps_spoofing"}
    out: dict = {}
    for k, v in row.items():
        if k in drop or v == "" or v is None:
            continue
        if k in bool_cols:
            out[k] = str(v).strip().lower() in ("1", "true", "yes")
        elif k == "track_confidence":
            out[k] = float(v)
        else:
            out[k] = v
    return out


def _score_holdout(api, platform_id: int, holdout_csv: Path) -> None:
    if not holdout_csv.exists():
        print(f"  (holdout {holdout_csv} not found — skipping scored holdout)")
        return
    with holdout_csv.open() as fh:
        rows = list(csv.DictReader(fh))
    n = len(rows)
    correct = certified = query_failed = over_permit = 0
    for row in rows:
        truth = row["decision"]
        facts = _coerce(row)
        try:
            report = api.platforms.query(platform_id, query=QUERY_TEXT, facts=facts)
        except AmbertraceError:
            # A verified fail-closed refusal is a MISS, not a crash.
            query_failed += 1
            continue
        if report.get("proof_checked"):
            certified += 1
        decision = _decision(report)
        if decision == truth:
            correct += 1
        # Over-permit = a track the ground truth escalates that the gate clears
        # (the unsafe direction for a triage gate).
        elif truth == "escalate" and decision == "clear":
            over_permit += 1
    acc = (correct / n * 100) if n else 0.0
    print(f"\n  Holdout: {correct}/{n} correct ({acc:.0f}%)  "
          f"cert={certified}/{n}  query_failed={query_failed}  over_permit={over_permit}")
    print(f"  Targets: >= 98% accuracy, cert {n}/{n}, 0 over-permit "
          f"-> {'PASS' if (acc >= 98 and certified == n and over_permit == 0) else 'CHECK'}")


def run_cross_domain_cueing_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Generate it with "
              f"`python gen_fused_tracks.py`.", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating cross-domain cueing (fused-track triage) domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading fused-track data (features only)")
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

    print_section(5, total, "Proving the cross-cues, then scoring the labelled holdout")
    showcase_ok = all(
        _show(api, platform["id"], label, facts, expected)
        for label, expected, facts in SHOWCASE_TRACKS
    )
    print(f"\n  Showcase cross-cue proof: {'ALL OK' if showcase_ok else 'MISMATCH — see above'}")
    if not args.no_holdout:
        _score_holdout(api, platform["id"], args.holdout)

    print(f"\nDone. Platform {platform['id']} is live. Tier-0 conditional claim: every "
          "cross-cued escalation is provably correct GIVEN the caller-derived cue "
          "(pre-joined outside the proof; Tier 1 brings the join inside). Synthetic data.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-Domain Cueing — AmberTrace AI verified multi-domain fusion triage demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--holdout", type=Path, default=DEFAULT_HOLDOUT)
    parser.add_argument("--no-holdout", action="store_true",
                        help="skip the 50-row labelled-holdout scoring (showcase rows only)")
    args = parser.parse_args()
    run_demo(run_cross_domain_cueing_demo, args)


if __name__ == "__main__":
    main()
