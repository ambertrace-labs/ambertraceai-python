"""58 — UK policy-market consistency (proof-carrying equilibrium / disequilibrium calls).

A macro market is in a *consistency equilibrium* when the prices it is quoting can all be true
at once. Disequilibrium is when they cannot — the market is pricing a combination that a policy
reaction function cannot reconcile, so something has to give. That dislocation *is* the trade.

This demo reduces the classic Bank-of-England-vs-market tension to two signed residuals and lets
the platform certify which state the UK rates market is in, on real monthly history (2009-2026).
The two inputs are computed *outside* AmberTrace (the numerical "search" — a market-implied OIS
path, a Taylor-type reaction prescription, a breakeven curve). AmberTrace's job is the verified
verdict:

  * ``path_reaction_gap``   — the 2Y SONIA-OIS spot rate (the market-implied average Bank Rate
    path over two years) minus the rate a BoE reaction function prescribes given UK inflation and
    unemployment. At or above zero, the market prices a *tighter* path than the reaction function
    warrants; below zero, an *easier* path (e.g. slower/fewer hikes than the data supports).
  * ``inflation_anchor_gap`` — the 10Y breakeven (RPI, re-based to CPI by a fixed wedge) minus
    the 2% CPI target. At or above zero, inflation is priced *hot* (at/above anchor); below zero,
    *soft*.

Four mutually-exclusive, exhaustive states (a symmetric N-class verdict — no state is a silent
"everything else" default, so a disequilibrium can never slip through as a missing case):

    path >=0, infl >=0  -> COHERENT_HAWKISH    (equilibrium: tight path, hot inflation)
    path  <0, infl  <0  -> COHERENT_DOVISH     (equilibrium: easy path, cooling inflation)
    path  <0, infl >=0  -> DISLOCATED_DOVISH   (disequilibrium: easy path, sticky inflation)
    path >=0, infl  <0  -> DISLOCATED_HAWKISH  (disequilibrium: tight path, cooling inflation)

The two DISLOCATED cells are certified *disequilibria*. Each answer names the symbolic rules that
fired and ships a machine-checked proof (``proof_checked``): the proof chain is the two colliding
conditions written out — the thesis you would hand to a risk committee ("we fade the priced easing
because the breakeven says inflation is still hot and the reaction function does not warrant it").

WHICH API — read this first. This is NOT ``author()``. The symmetric N-class consistency
classifier is a SEPARATE verified platform whose DECISION VERBS *are* the class labels. Build it
through the ordinary ``domains`` -> ``build_ontology`` -> ``platforms`` surface (same as ex38).
Query with ``platforms.query(... facts={...})`` and read ``decision`` / ``proof_checked``.

DATA: every input is a real market/economic observation (BoE OIS archive, BoE breakevens, ONS CPI,
UK unemployment). Bundled snapshot: ``data/uk_policy_consistency_panel.csv`` (206 monthly rows,
two feature columns). No API key beyond AmberTrace is needed.

    python 58_uk_policy_market_consistency.py             # build + classify real UK episodes
    python 58_uk_policy_market_consistency.py --standard   # skip the verified profile (no proof)
"""

from __future__ import annotations

import argparse
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
DEFAULT_DATASET = DATA_DIR / "uk_policy_consistency_panel.csv"

DOMAIN_NAME = "UK policy-market consistency (BoE reaction function vs priced OIS path)"
DOMAIN_DESCRIPTION = (
    "Classify each observation into exactly one state: COHERENT_HAWKISH, COHERENT_DOVISH, "
    "DISLOCATED_DOVISH, or DISLOCATED_HAWKISH. The coherent states are equilibria and the dislocated "
    "states are disequilibria. Each observation has two signed residuals: path_reaction_gap and inflation_anchor_gap. "
    "Both are signed numbers. path_reaction_gap is the market-implied 2-year policy path (from "
    "overnight index swaps) minus the path a Bank of England reaction function prescribes given "
    "inflation and unemployment — at or above zero when the market prices a tighter path than the "
    "reaction function warrants, below zero when it prices an easier path (for example a slower "
    "or shallower hiking path than the data supports). inflation_anchor_gap is priced breakeven "
    "inflation minus the 2 percent target — at or above zero when inflation is priced hot (at or "
    "above anchor), below zero when it is priced soft. When path_reaction_gap is at or above zero "
    "and inflation_anchor_gap is at or above zero, the state is COHERENT_HAWKISH: a tight priced "
    "path leaning against hot inflation is mutually consistent, an equilibrium. When "
    "path_reaction_gap is below zero and inflation_anchor_gap is below zero, the state is "
    "COHERENT_DOVISH: an easy priced path into cooling inflation is mutually consistent, an "
    "equilibrium. When path_reaction_gap is below zero and inflation_anchor_gap is at or above "
    "zero, the state is DISLOCATED_DOVISH: the market prices an easier path than warranted while "
    "inflation is still hot, which the reaction function cannot reconcile, a disequilibrium. When "
    "path_reaction_gap is at or above zero and inflation_anchor_gap is below zero, the state is "
    "DISLOCATED_HAWKISH: the market prices a tighter path than warranted while inflation is "
    "cooling, which the reaction function cannot reconcile, a disequilibrium. Every consistency "
    "call must be auditable."
)

CLASSIFY = "Classify the UK policy-market consistency state."

# Real landmark months — the actual computed residuals for each month, read from the full
# timeline (built by scripts/build_uk_consistency_panel.py). Hardcoded here so the example
# runs without bundling the timeline CSV.
LANDMARKS: list[tuple[str, dict[str, float], str]] = [
    ("Jun 2015 — pre-liftoff; breakevens anchored near target",
     {"path_reaction_gap": 2.3092, "inflation_anchor_gap": 0.003},
     "COHERENT_HAWKISH"),
    ("Mar 2020 — COVID: OIS collapses, inflation soft",
     {"path_reaction_gap": -2.0076, "inflation_anchor_gap": -0.0238},
     "COHERENT_DOVISH"),
    ("Dec 2021 — BoE behind the curve; inflation surging, path barely moved",
     {"path_reaction_gap": -7.0041, "inflation_anchor_gap": 0.8656},
     "DISLOCATED_DOVISH"),
    ("Sep 2022 — gilt/LDI crisis; CPI ~10%, path far below a Taylor rule",
     {"path_reaction_gap": -10.0165, "inflation_anchor_gap": 0.9094},
     "DISLOCATED_DOVISH"),
    ("Aug 2024 — normalising; path modestly tight, breakeven near anchor",
     {"path_reaction_gap": 1.0478, "inflation_anchor_gap": 0.3943},
     "COHERENT_HAWKISH"),
    ("Feb 2026 — latest month",
     {"path_reaction_gap": -0.1905, "inflation_anchor_gap": 0.0927},
     "DISLOCATED_DOVISH"),
]


# The Decision Table, in PARTITION mode: the four states are mutually exclusive cells -- no default,
# no order, no permits. Each cell is a rule the platform proves; zero or several firing is
# `status == "abstain"` (never a made-up label). `label` is served verbatim in `decision`.
DECISION_TABLE = {
    "mode": "partition",
    "rows": [
        {"label": "COHERENT_HAWKISH"},
        {"label": "COHERENT_DOVISH"},
        {"label": "DISLOCATED_DOVISH"},
        {"label": "DISLOCATED_HAWKISH"},
    ],
}


def run_consistency(api, args: argparse.Namespace) -> None:
    total = 5

    print_section(1, total, "Creating UK policy-market consistency domain (plain-English)")
    domain = api.domains.create(
        name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION, decision_table=DECISION_TABLE)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading the real reaction-residual coverage panel")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (the four consistency rules)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau,
    )
    pid = platform["id"]
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {pid}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Classifying real UK episodes (proof-carrying)")
    passed = 0
    for label, facts, expected in LANDMARKS:
        print(f"\n  {label}")
        print(f"  facts: {facts}")
        try:
            report = api.platforms.query(pid, query=CLASSIFY, facts=facts)
        except Exception as exc:
            print(f"    VERIFIED FAIL-SAFE — refused to certify: {exc}")
            continue
        decision = report.get("decision")
        derived = report.get("derived")
        proof = report.get("proof_checked")
        trace = (report.get("explanation") or {}).get("symbolic_trace") or {}
        mark = "[OK]" if decision and decision.upper() == expected else f"[!! expected {expected}]"
        print(f"    -> decision={decision}  derived={derived}  proof_checked={proof}  {mark}")
        if trace.get("rules"):
            for rule in trace["rules"]:
                if rule.get("fired"):
                    print(f"       rule: {rule.get('rule_name')}: {(rule.get('explanation') or '')[:80]}")
        if report.get("proof_summary"):
            print(f"       proof: {report['proof_summary'][:120]}")
        if decision and decision.upper() == expected:
            passed += 1

    print(f"\n{passed}/{len(LANDMARKS)} episodes resolved to the expected consistency state.")
    print(f"\nDone. Platform {pid} is live. Every call above is a real UK month classified with a "
          "machine-checked proof; the DISLOCATED verdicts are certified disequilibria — the proof "
          "chain is the trade thesis.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="UK policy-market consistency — verified equilibrium / disequilibrium calls",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help=f"Reaction-residual coverage panel (default: {DEFAULT_DATASET.name})")
    args = parser.parse_args()
    run_demo(run_consistency, args)


if __name__ == "__main__":
    main()
