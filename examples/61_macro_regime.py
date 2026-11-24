"""61 -- Macro regime: proof-carrying growth x inflation quadrant classification.

The macro cycle in one map: real GDP growth momentum against its recent trend on
one axis, CPI inflation momentum against its recent trend on the other, giving
four mutually-exclusive quadrants -- REFLATION, GOLDILOCKS, STAGFLATION,
DEFLATION (the investment-clock regimes).

This demo writes those four definitions in *plain English*, lets the platform
induce the ontology, builds a **verified** platform, and classifies conditions
so every regime call carries a machine-checked proof (``proof_checked``).

Unlike a black-box regime model, each answer names the symbolic rules that fired
and ships a proof certificate -- and the four cells are a *symmetric N-class*
verdict, so no regime is a silent "everything else" default.

WHICH API -- this uses the ordinary ``domains`` -> ``build_ontology`` ->
``platforms`` surface (the same shape as ``38_symmetric_multiclass_classifier``).
There is no new SDK method -- the classifier IS the domain platform. Query it
with ``platforms.query(...)`` and read ``report["decision"]`` (the winning
label) and ``report["proof_checked"]``.

DATA: momentum features (growth / inflation measured against their multi-year
trend) derived from public-domain FRED series (real GDP ``GDPC1``, CPI
``CPIAUCSL``); bundled as ``data/macro_regime_momentum.csv``. No API key beyond
AmberTrace is needed.

    python 61_macro_regime.py                    # build + classify the 4 quadrants
    python 61_macro_regime.py --standard         # skip the verified profile
    python 61_macro_regime.py --platform-id 42   # reuse an already-built platform
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_amber_report,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
PANEL = DATA_DIR / "macro_regime_momentum.csv"

DOMAIN_NAME = "Macro regime (growth x inflation quadrant)"
DOMAIN_DESCRIPTION = (
    "Classify each observation into exactly one macroeconomic regime: reflation, goldilocks, "
    "stagflation, or deflation. Each observation has two signed momentum indicators: real GDP growth momentum (growth_vs_trend) and CPI inflation momentum "
    "(infl_vs_trend). Both are signed numbers -- at or above zero when the indicator is "
    "running above its recent trend, below zero when it is running below trend. When "
    "growth_vs_trend is at or above zero and infl_vs_trend is at or above zero, the regime "
    "is REFLATION (growth and inflation both rising). When growth_vs_trend is at or above "
    "zero and infl_vs_trend is below zero, the regime is GOLDILOCKS (growth rising, "
    "inflation cooling). When growth_vs_trend is below zero and infl_vs_trend is at or "
    "above zero, the regime is STAGFLATION (growth slowing, inflation rising). When "
    "growth_vs_trend is below zero and infl_vs_trend is below zero, the regime is DEFLATION "
    "(growth and inflation both cooling). Every regime classification must be auditable."
)

# The Decision Table, in PARTITION mode: the four states are mutually exclusive cells -- no default,
# no order, no permits. Each cell is a rule the platform proves; zero or several firing is
# `status == "abstain"` (never a made-up label). `label` is served verbatim in `decision`.
DECISION_TABLE = {
    "mode": "partition",
    "rows": [
        {"label": "reflation"},
        {"label": "goldilocks"},
        {"label": "stagflation"},
        {"label": "deflation"},
    ],
}

CLASSIFY = "Classify the macroeconomic regime."

# One illustrative observation per quadrant (growth_vs_trend, infl_vs_trend).
SCENARIOS: list[tuple[str, dict[str, float], str]] = [
    ("growth rising, inflation rising",
     {"growth_vs_trend": 1.2, "infl_vs_trend": 0.8}, "reflation"),
    ("growth rising, inflation cooling",
     {"growth_vs_trend": 1.1, "infl_vs_trend": -0.6}, "goldilocks"),
    ("growth slowing, inflation rising",
     {"growth_vs_trend": -1.3, "infl_vs_trend": 0.9}, "stagflation"),
    ("growth slowing, inflation cooling",
     {"growth_vs_trend": -1.0, "infl_vs_trend": -0.7}, "deflation"),
]


def _latest_observation(path: Path) -> tuple[str, dict[str, float]] | None:
    """Read the most recent quarter from the timeline CSV (if bundled).

    The timeline is NOT required -- it is a companion artifact for historical
    back-testing. When present, its last row is classified as "today".
    """
    if not path.exists():
        return None
    rows = list(csv.DictReader(path.open()))
    if not rows:
        return None
    last = rows[-1]
    return last["date"], {
        "growth_vs_trend": float(last["growth_vs_trend"]),
        "infl_vs_trend": float(last["infl_vs_trend"]),
    }


def _classify(api, platform_id: int, label: str, facts: dict, expected: str) -> str:
    """Query one cell; read the winning label from ``decision``."""
    try:
        report = api.platforms.query(
            platform_id, query=CLASSIFY, facts=facts,
        )
    except Exception as exc:
        print(f"    VERIFIED FAIL-SAFE -- refused to certify: {exc}")
        return "error"
    decision = report.get("decision")
    proof = report.get("proof_checked")
    mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
    print(f"    -> {str(decision).upper():14s} {mark}  proof_checked={proof}")
    return str(decision)


def run_macro_regime(api, args: argparse.Namespace) -> None:
    total = 5

    if args.platform_id:
        platform = api.platforms.get(args.platform_id)
        print(f"  reusing platform {args.platform_id} ({platform.get('status')})")
        _classify_all(api, args.platform_id)
        return

    print_section(1, total, "Creating macro-regime domain (plain-English quadrant policy)")
    domain = api.domains.create(
        name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION, decision_table=DECISION_TABLE)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading the growth x inflation momentum panel")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(PANEL))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (the four quadrant rules)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    pid = platform["id"]
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {pid}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Classifying the regime (proof-carrying)")
    _classify_all(api, pid)


def _classify_all(api, platform_id: int) -> None:
    """Classify each quadrant scenario and report results."""
    passed = 0
    for label, facts, expected in SCENARIOS:
        print(f"\n  {label}  ->  {facts}")
        decision = _classify(api, platform_id, label, facts, expected)
        passed += decision == expected

    # If the timeline CSV is bundled alongside the momentum panel, classify
    # its most recent quarter as "today".
    timeline = DATA_DIR / "macro_regime_timeline.csv"
    latest = _latest_observation(timeline)
    if latest is not None:
        date, facts = latest
        print(f"\n  Today -- latest real quarter ({date})  ->  {facts}")
        try:
            report = api.platforms.query(platform_id, query=CLASSIFY, facts=facts)
            print_amber_report(report)
        except Exception as exc:
            print(f"    VERIFIED FAIL-SAFE -- refused to certify: {exc}")

    print(f"\n{passed}/{len(SCENARIOS)} quadrant cells resolved to the expected regime.")
    print("Done. Every regime call above carries a machine-checked proof.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Macro regime -- verified growth x inflation quadrant classification",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--platform-id", type=int, default=None,
        help="reuse an already-built platform (skip the build)",
    )
    args = parser.parse_args()
    run_demo(run_macro_regime, args)


if __name__ == "__main__":
    main()
