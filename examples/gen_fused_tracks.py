"""Cross-domain cueing dataset — unified ``fused_track`` schema (synthetic, seeded).

Generates the data for the DIANA Tier-0 cross-domain-cueing demo
(``25_cross_domain_cueing.py``). One unified entity carries BOTH air and maritime
surface tracks through a single verified core; the two cross-domain cue booleans
(``grid_has_confirmed_maritime_exclusion_breach``, ``grid_has_gps_spoofing``)
enter as ordinary declared inputs — they are **pre-joined by an upstream fusion /
correlation layer**, OUTSIDE the proof (that is the Tier-0 honest claim; Tier 1
brings the correlation inside the proof — see
``../AmbertraceAIUser/docs/design-cross-domain-cueing.md`` §6).

The triage ground truth is computed by :func:`reference_policy`, the same policy
the demo authors in plain English, so the platform's verdicts can be scored
against known-correct labels.

Schema (``fused_track``):
  track_id                                       id (dropped from features)
  domain                  air | maritime         discriminator
  grid_square             enum                   spatial key (the upstream join key)
  position_source         gps | radar | ais | sonar   sensor providing the position
  identification          unidentified | friendly | hostile | unknown
  in_exclusion_zone       bool                   air restricted-zone / maritime breach
  track_confidence        float [0..1]           sensor/fusion confidence
  grid_has_confirmed_maritime_exclusion_breach   bool   cross-cue from Domain B (pre-joined)
  grid_has_gps_spoofing                          bool   cross-cue from Domain C (pre-joined)

Policy (first matching rule wins; identical to the demo's English authoring):
  escalate when a confirmed maritime exclusion breach is present in the grid AND unidentified  # cross-cue 1, TOP precedence
  escalate when in an exclusion zone AND unidentified                                          # standard triage
  escalate when hostile
  monitor  when unidentified AND track_confidence >= 0.6
  monitor  when in an exclusion zone
  otherwise clear

  (separate soft obligation)  requires_human_review := grid_has_gps_spoofing AND position_source == gps
  (separate derived flag)     position_trusted       := NOT (grid_has_gps_spoofing AND position_source == gps)

    python gen_fused_tracks.py               # 20k feature rows + 50-row holdout
    python gen_fused_tracks.py --rows 5000
    python gen_fused_tracks.py --report      # label mix only
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_ROWS = 20_000
HOLDOUT_ROWS = 50
SEED = 7373

GRID_SQUARES = ["GS-11", "GS-12", "GS-13", "GS-21", "GS-22", "GS-23", "GS-31", "GS-32"]
AIR_SOURCES = ["gps", "radar"]
MARITIME_SOURCES = ["ais", "sonar"]
IDENTIFICATIONS = ["unidentified", "friendly", "hostile", "unknown"]

COLUMNS = [
    "track_id", "domain", "grid_square", "position_source", "identification",
    "in_exclusion_zone", "track_confidence",
    "grid_has_confirmed_maritime_exclusion_breach", "grid_has_gps_spoofing",
    "decision", "requires_human_review", "position_trusted",
]
LABEL_COLUMNS = ("decision", "requires_human_review", "position_trusted")
FEATURE_COLUMNS = [c for c in COLUMNS if c not in LABEL_COLUMNS]


def reference_policy(r: dict) -> tuple[str, bool, bool]:
    """Ground-truth triage on a fused track.

    Returns ``(decision, requires_human_review, position_trusted)``:

    * ``decision``              the hard triage tier (first matching rule),
    * ``requires_human_review`` the separate soft obligation,
    * ``position_trusted``      the derived sensor-trust flag (modelled as a
                                first-class derivation, NOT an input mutation).
    """
    unidentified = r["identification"] == "unidentified"
    hostile = r["identification"] == "hostile"
    in_zone = bool(r["in_exclusion_zone"])
    maritime_breach = bool(r["grid_has_confirmed_maritime_exclusion_breach"])
    conf = float(r["track_confidence"])

    spoofed_position = bool(r["grid_has_gps_spoofing"]) and r["position_source"] == "gps"
    position_trusted = not spoofed_position
    requires_human_review = spoofed_position

    # Hard verdict — first matching rule wins.
    if maritime_breach and unidentified:          # cross-cue 1 — TOP precedence
        decision = "escalate"
    elif in_zone and unidentified:                # standard triage
        decision = "escalate"
    elif hostile:
        decision = "escalate"
    elif unidentified and conf >= 0.6:
        decision = "monitor"
    elif in_zone:
        decision = "monitor"
    else:
        decision = "clear"

    return decision, requires_human_review, position_trusted


def _synth_row(rng: random.Random, track_id: int) -> dict:
    """One diverse, reproducible fused-track record (no external data)."""
    domain = "air" if rng.random() < 0.6 else "maritime"
    grid = rng.choice(GRID_SQUARES)
    if domain == "air":
        source = rng.choices(AIR_SOURCES, weights=[55, 45])[0]
    else:
        source = rng.choices(MARITIME_SOURCES, weights=[60, 40])[0]
    identification = rng.choices(IDENTIFICATIONS, weights=[28, 45, 12, 15])[0]
    in_zone = rng.random() < 0.30
    conf = round(rng.uniform(0.30, 0.99), 3)
    # Cross-domain cues: pre-joined booleans from the fusion layer. A maritime
    # exclusion breach correlated to this grid is uncommon; GPS spoofing rarer.
    maritime_breach = rng.random() < 0.14
    gps_spoofing = rng.random() < 0.10

    rec = {
        "track_id": track_id,
        "domain": domain,
        "grid_square": grid,
        "position_source": source,
        "identification": identification,
        "in_exclusion_zone": in_zone,
        "track_confidence": conf,
        "grid_has_confirmed_maritime_exclusion_breach": maritime_breach,
        "grid_has_gps_spoofing": gps_spoofing,
    }
    decision, review, trusted = reference_policy(rec)
    rec["decision"] = decision
    rec["requires_human_review"] = review
    rec["position_trusted"] = trusted
    return rec


def build_dataset(target_rows: int, *, seed: int = SEED) -> list[dict]:
    """Build the synthetic + reproducible fused-track dataset."""
    rng = random.Random(seed)
    return [_synth_row(rng, i + 1) for i in range(target_rows)]


def _write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore",
                           lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (int(v) if isinstance(v, bool) else v) for k, v in r.items()})


def distribution(rows: list[dict]) -> dict:
    n = len(rows) or 1
    tiers = {"clear": 0, "monitor": 0, "escalate": 0}
    review = 0
    untrusted = 0
    for r in rows:
        tiers[r["decision"]] += 1
        review += 1 if r["requires_human_review"] else 0
        untrusted += 0 if r["position_trusted"] else 1
    out = {k: round(100 * v / n, 1) for k, v in tiers.items()}
    out["requires_human_review_pct"] = round(100 * review / n, 1)
    out["position_untrusted_pct"] = round(100 * untrusted / n, 1)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the cross-domain-cueing fused-track dataset (synthetic)")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS, help="target feature row count")
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--report", action="store_true", help="print the label distribution only")
    args = parser.parse_args()

    rows = build_dataset(args.rows + HOLDOUT_ROWS, seed=args.seed)
    print(f"Label distribution ({len(rows)} rows): {distribution(rows)}")
    if args.report:
        return
    train, holdout = rows[:-HOLDOUT_ROWS], rows[-HOLDOUT_ROWS:]
    _write_csv(DATA_DIR / "fused_tracks.csv", train, FEATURE_COLUMNS)
    _write_csv(DATA_DIR / "fused_tracks_holdout.csv", holdout, COLUMNS)
    print(f"Wrote {len(train)} feature rows -> data/fused_tracks.csv (no labels)")
    print(f"Wrote {len(holdout)} held-out labelled rows -> data/fused_tracks_holdout.csv")


if __name__ == "__main__":
    main()
