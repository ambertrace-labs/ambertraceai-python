"""38 — Symmetric N-class classifier (verified multi-class / multiclass classification).

A VERIFIED DOMAIN PLATFORM that classifies an observation into ONE of N mutually
exclusive labels — an N-way / symmetric multi-class classification — with a
machine-checked proof for every answer.

WHICH API — read this first. This is NOT ``author()``. ``author()`` is the Agent
Policy Gate: a single per-org PERMIT/DENY obligation gate (its only outcomes are
permit / deny / indeterminate / unavailable). A symmetric N-class classifier is a
different shape entirely: it is a SEPARATE verified platform whose DECISION VERBS
*are* the class labels (here: reflation / goldilocks / stagflation / deflation).
It does not touch a permit/deny gate — so a trade gate's ``decision_vocabulary``
being ``None`` is unrelated to it. You author it through the ordinary
``domains`` → ``build_ontology`` → ``platforms`` surface — there is no
``multiclass`` model_type and no new SDK method; the classifier IS the domain
platform. Query it with ``platforms.query(...)`` and read ``report["decision"]``
(the winning label) and ``report["proof_checked"]``.

THE LOAD-BEARING PART is the English ``description``. To build a symmetric N-class
classifier that resolves every cell, phrase it so the builder can synthesise one
derived-outcome rule per label:

  1. Define each AXIS with an explicit threshold AND an ``otherwise`` clause, so the
     axis is a total two-valued (or m-valued) partition:
     "growth is firm when real GDP growth is at least 2.0 percent, otherwise soft".
  2. Define each LABEL as a CONJUNCTION of axis states (one label per cell of the
     grid): "reflation is firm growth with elevated inflation".
  3. State completeness explicitly: "Every observation must be classified into
     exactly one regime." — this is what makes it a total, mutually-exclusive
     partition rather than a set of overlapping flags.

This example builds the canonical 2×2 macro-regime grid (two axes, four labels)
from that English and proves each of the four cells resolves to its label with a
checked proof. It is the discoverable, copy-me template for any flat N-way or
k-axis-grid classifier (see the "envelope" note at the foot of this file).

DATA: a small SEEDED SYNTHETIC features-only panel generated on first run. It only
has to DECLARE the two feature columns (``real_gdp_growth``, ``cpi_inflation_yoy``)
and span their range — there are NO labels in the data (the labels come from the
English description, not from supervision). No external key is needed.

    python 38_symmetric_multiclass_classifier.py                 # build + classify the 4 cells
    python 38_symmetric_multiclass_classifier.py --standard      # skip the verified profile
    python 38_symmetric_multiclass_classifier.py --platform-id 42  # reuse a built classifier
"""

from __future__ import annotations

import argparse
import csv
import random
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
PANEL = DATA_DIR / "macro_regime_panel.csv"          # seeded features-only on first run

# The two axis thresholds — kept in one place so the data, the English and the
# expected-label table below can never drift apart.
GROWTH_FIRM_MIN = 2.0          # real_gdp_growth >= 2.0 percent  -> firm, else soft
INFLATION_ELEVATED_MIN = 2.5   # cpi_inflation_yoy >= 2.5 percent -> elevated, else contained

DOMAIN_NAME = "Macro Regime"
# The LOAD-BEARING English. Axes with explicit thresholds + "otherwise"; each of the
# four labels is a conjunction of the two axis states; explicit exactly-one completeness.
DOMAIN_DESCRIPTION = (
    "Macro regime classifier. Classify the economy into one of four regimes from two axes: "
    "growth is firm when real GDP growth is at least 2.0 percent, otherwise soft; inflation is "
    "elevated when CPI year-on-year is at least 2.5 percent, otherwise contained. Reflation is "
    "firm growth with elevated inflation; goldilocks is firm growth with contained inflation; "
    "stagflation is soft growth with elevated inflation; deflation is soft growth with contained "
    "inflation. Every observation must be classified into exactly one regime."
)

# The four cells of the 2x2 grid and the label each MUST resolve to.
# (label description, facts, expected regime)
SUITE: list[tuple[str, dict, str]] = [
    ("firm growth (gdp 3.2 >= 2.0), elevated inflation (cpi 3.4 >= 2.5)",
     {"real_gdp_growth": 3.2, "cpi_inflation_yoy": 3.4}, "reflation"),
    ("firm growth (gdp 3.0 >= 2.0), contained inflation (cpi 1.8 < 2.5)",
     {"real_gdp_growth": 3.0, "cpi_inflation_yoy": 1.8}, "goldilocks"),
    ("soft growth (gdp 0.5 < 2.0), elevated inflation (cpi 4.0 >= 2.5)",
     {"real_gdp_growth": 0.5, "cpi_inflation_yoy": 4.0}, "stagflation"),
    ("soft growth (gdp 0.8 < 2.0), contained inflation (cpi 1.2 < 2.5)",
     {"real_gdp_growth": 0.8, "cpi_inflation_yoy": 1.2}, "deflation"),
]


def _regime_for(gdp: float, cpi: float) -> str:
    """The ground-truth partition — used only to seed a realistic features-only panel."""
    firm = gdp >= GROWTH_FIRM_MIN
    elevated = cpi >= INFLATION_ELEVATED_MIN
    if firm and elevated:
        return "reflation"
    if firm and not elevated:
        return "goldilocks"
    if not firm and elevated:
        return "stagflation"
    return "deflation"


def _generate_panel(path: Path, n: int = 1200) -> None:
    """Write a features-only panel that DECLARES the two axis columns.

    ONLY the two feature columns are written — there is NO regime/label column. The
    class labels come from the English ``description`` (the builder synthesises one
    derived-outcome rule per label), not from supervision. We seed >=1000 rows so
    both axes span their full range on both sides of every threshold, which lets the
    builder ground each of the four cells against real data.
    """
    rng = random.Random(20260707)
    fields = ["real_gdp_growth", "cpi_inflation_yoy"]
    counts: dict[str, int] = {}
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for _ in range(n):
            gdp = round(rng.uniform(-2.0, 5.0), 2)      # spans both sides of 2.0
            cpi = round(rng.uniform(0.0, 6.0), 2)       # spans both sides of 2.5
            counts[_regime_for(gdp, cpi)] = counts.get(_regime_for(gdp, cpi), 0) + 1
            w.writerow({"real_gdp_growth": gdp, "cpi_inflation_yoy": cpi})
    # Confirm every cell of the grid is populated in the seed (data-sufficiency).
    print(f"  generated {n} features-only rows -> {path}  (cell coverage: {counts})")


def _classify(api, platform_id: int, label: str, facts: dict, expected: str) -> str:
    """Query one cell; read the winning label from ``decision`` (not permit/deny)."""
    try:
        report = api.platforms.query(
            platform_id, query="Classify the macro regime.", facts=facts)
    except Exception as exc:  # a verified fail-safe refusal is an outcome, not a crash
        print(f"    VERIFIED FAIL-SAFE — refused to certify: {exc}")
        return "error"
    decision = report.get("decision")
    proof = report.get("proof_checked")
    mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
    print(f"    -> {str(decision).upper():12s} {mark}  proof_checked={proof}")
    return str(decision)


def _run_cells(api, platform_id: int) -> None:
    passed = 0
    for label, facts, expected in SUITE:
        print(f"\n  {label}")
        decision = _classify(api, platform_id, label, facts, expected)
        passed += decision == expected
    print(f"\n{passed}/{len(SUITE)} cells resolved to the expected regime.")
    print("Done. Each answer above is a proof-carrying multi-class label: the winning "
          "regime is the platform's DECISION verb, and proof_checked=True means the "
          "kernel certified it against the derived-outcome partition — no permit/deny "
          "gate involved.")


def run_multiclass_demo(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Building the macro-regime classifier domain (features only)")
    print(f"  N-CLASS DESCRIPTION (the load-bearing English):\n    {DOMAIN_DESCRIPTION}\n")
    if args.platform_id:
        platform = api.platforms.get(args.platform_id)
        print(f"  reusing classifier platform {args.platform_id} ({platform.get('status')})")
        print_section(4, total, "Classifying each cell of the 2x2 grid (features -> checked label)")
        _run_cells(api, args.platform_id)
        return

    if not PANEL.exists():
        _generate_panel(PANEL)
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(PANEL))
    print_dataset(dataset)

    print_section(2, total, "Building ontology (one derived-outcome rule per regime label)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=14)

    print_section(3, total, "Building verified classifier platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(4, total, "Classifying each cell of the 2x2 grid (features -> checked label)")
    _run_cells(api, platform["id"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Symmetric N-class / multiclass classifier — a verified domain platform")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--platform-id", type=int, default=None,
                        help="reuse an already-built classifier platform (skip the build)")
    args = parser.parse_args()
    run_demo(run_multiclass_demo, args)


if __name__ == "__main__":
    main()

# --- Complexity envelope (how far this template scales) ----------------------
#
# The same three-part English recipe (axes-with-thresholds-and-otherwise, one
# label per conjunction-of-axis-states, explicit exactly-one completeness) is the
# general form for ANY symmetric multi-class classifier — not just this 2x2 grid.
# Two shapes, both authored the same way:
#
#   * FLAT N-way (N labels, one condition each): "the tier is gold when ...,
#     silver when ..., bronze when ...; every account is exactly one tier."
#     SOUND for flat N up to ~6-8 labels through the real build.
#   * k-AXIS GRID (m values per axis -> m**k cells): author it COMPOSITIONALLY —
#     k axis-classifiers plus one label-per-cell layer — so it stays O(k*m) rules,
#     not O(m**k). SOUND for grids around k=2,m=3 (9 cells) / k=3,m=2 (8 cells).
#
# Above that envelope the platform degrades GRACEFULLY (it abstains / returns a
# fail-safe rather than silently mis-labelling) — the binding constraint is the
# LLM proposer's authoring reliability, not the verified kernel. Keep the axes
# few and each label a clean conjunction and the classifier stays certifiable.
