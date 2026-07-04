"""35 — Geopolitical risk (GPR) macro forecast (let the SYSTEM pick the drivers; the honest read).

Same premise as the other macro demos (GS10, S&P 500, Bitcoin, inflation, credit, GDP): don't
hand-pick features. Give the platform a BROAD, neutral panel of US macro series and let it tell
you which ones explain the target — with the readable rules to back it.

Geopolitical risk is the honest one. Unlike the other targets it is largely EXOGENOUS — driven by
world events, not by the macro panel — so expect only modest macro explanatory power. That is the
finding, not a failure: it is exactly why a news-ingestion signal (Phase 2) is the real driver.
The oil price is the macro series most likely to co-move (geopolitical shocks hit oil), so watch
whether the system surfaces it in the rules.

  1. Upload a bundled MONTHLY macro panel whose target is GPR — the Caldara-Iacoviello
     Geopolitical Risk index, a text-based index over major-newspaper coverage of geopolitical
     tensions (``data/geopol_macro_panel.csv``; the FRED macro panel merged with the public GPR
     series; all public / public-domain; the panel is bundled and fully reproducible).
  2. Build a verified platform and train a MONTHLY forecaster on GPR with autoregression turned
     OFF (``autoregressive="none"``) — so the model must explain GPR through the macro drivers
     rather than leaning on its own (persistent) recent level.
  3. Read back what the SYSTEM selected:
       - neural feature importance, aggregated by base series (which macro series it keeps);
       - the symbolic forecaster's induced WHEN->THEN driver rules (the WHY);
       - the neuro-symbolic discovery pass (does a correction layer beat the neural model?).

Honest framing: the value is the EXPLANATION and, here, an honest read on HOW LITTLE macro moves
geopolitical risk. GPR is persistent, so its own recent level is informative; the default keeps
autoregression OFF to keep the driver story honest — pass ``--autoregressive limited`` to let the
model use recent GPR as a persistence baseline.

LIVE RESULTS (bundled snapshot; confirm with a fresh run): forecast ~258 from a ~254 baseline
over ~411 monthly rows (1992–2026). The kept drivers are led by the short rate (TB3MS), payrolls
(PAYEMS) and labour participation (CIVPART); ~11 readable WHEN->THEN rules, with the oil price
(MCOILWTICO) surfacing in the driver rules as expected. The headline is modest macro explanatory
power — the honest point of the demo.

DATA: the GPR index is public (Caldara & Iacoviello, matteoiacoviello.com — cite on reuse); the
macro panel is public-domain FRED. Bundled snapshot; no API key needed to run this demo.

    python 35_geopolitical_risk_macro_forecast.py             # build on the bundled snapshot
    python 35_geopolitical_risk_macro_forecast.py --standard  # skip the verified profile
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "geopol_macro_panel.csv"
TARGET = "GPR"

DOMAIN_NAME = "Geopolitical risk (system feature selection)"
# Keep this a PLAIN forecasting description (mirroring gs10/inflation/gdp). Editorial or
# category-flavoured wording (e.g. "geopolitical risk is exogenous") leads the ontology builder
# to invent an ungroundable classifier and the build fails with a dangling head. The exogeneity
# framing lives in the module docstring and the step-5 output, NOT here.
DOMAIN_DESCRIPTION = (
    "Forecast GPR, the Caldara-Iacoviello Geopolitical Risk index, one month ahead from a broad "
    "panel of US macro indicators: short rates and credit (FEDFUNDS, GS2, GS1, TB3MS, GS10, AAA, "
    "BAA), prices (CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour (UNRATE, PAYEMS, CIVPART), money "
    "and credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), "
    "consumer sentiment (UMCSENT) and the oil price (MCOILWTICO). Let the data decide which "
    "drivers matter for geopolitical risk."
)

# Split an engineered feature name back to its base series, e.g. HOUST_lag_1 -> HOUST.
_SUFFIX_RE = re.compile(r"_(rollmean|rollstd|rollchg|rolldev|pctchg|lag|roc|chg|diff|zscore)")


def _aggregate_importance(feature_importance: list) -> list[tuple[str, float]]:
    """Sum engineered-feature importance back to base series (drop _lag_/_roc_/... suffixes)."""
    base: dict[str, float] = defaultdict(float)
    for x in feature_importance or []:
        name = x.get("feature") if isinstance(x, dict) else x[0]
        imp = (x.get("importance") if isinstance(x, dict) else x[1]) or 0
        base[_SUFFIX_RE.split(name)[0]] += imp
    return sorted(base.items(), key=lambda kv: -kv[1])


def _print_fit(prediction: dict[str, Any]) -> None:
    """Print the backtest FIT (level + month-to-month change + skill context)."""
    model = (prediction.get("explanation") or {}).get("model") or {}
    metrics = model.get("metrics") or {}
    level = metrics.get("level") or {}
    transformed = metrics.get("transformed") or {}
    r2 = level.get("r2", model.get("r2"))
    rmse = level.get("rmse", model.get("rmse"))
    skill = metrics.get("skill_vs_persistence", model.get("skill_vs_persistence"))
    print(f"  fit (level): R^2={r2}, RMSE={rmse}")
    if isinstance(transformed.get("r2"), (int, float)):
        print(f"  fit (month-to-month change): R^2={transformed.get('r2')}")
    if isinstance(skill, (int, float)):
        print(f"  (skill_vs_persistence={skill:+.3f} — context only; on geopolitical risk expect "
              "little macro skill, which is the honest point of this demo.)")


def run_geopol_forecast(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found.", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating domain + uploading the bundled monthly GPR macro panel")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology + verified platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    # autoregressive="none": force the model to EXPLAIN GPR through the macro panel rather than
    # leaning on its own (persistent) recent level. Pass --autoregressive limited for a
    # persistence baseline. Frequency is monthly.
    cfg = api.predictions.create_config(
        pid, mode="timeseries", target_field=TARGET, time_index_field="date",
        horizon=args.horizon, frequency="monthly", model_type="gbt",
        autoregressive=args.autoregressive)
    cfg = train_prediction_model(api, pid, cfg["id"])

    print_section(3, total, "What the SYSTEM selected — neural feature importance")
    ar_note = ("drivers only — no GPR own-history features"
               if args.autoregressive == "none" else args.autoregressive)
    print(f"  autoregressive={args.autoregressive} ({ar_note})")
    base = api.predictions.predict(pid, prediction_config_id=cfg["id"])
    _print_fit(base)
    ranking = _aggregate_importance((base.get("explanation") or {}).get("feature_importance"))
    kept = [(b, i) for b, i in ranking if i > 0 and b != "date"]
    print(f"  the model kept {len(kept)} macro series with non-zero importance "
          "(aggregated by base series):")
    for b, imp in kept:
        print(f"    {b:12s} {imp:.4f}")

    print_section(4, total, "Symbolic forecaster — induced WHEN-THEN driver rules")
    sf = api.predictions.symbolic_forecast(
        pid, prediction_config_id=cfg["id"], verified=not args.standard)
    why = sf.get("why") or []
    print(f"  {len(why)} driver rules induced; baseline={sf.get('baseline')} "
          f"forecast={(sf.get('forecast') or {}).get('value')}")
    for w in sorted(why, key=lambda x: -abs(x.get("contribution") or 0))[:8]:
        d = str(w.get("driver"))[:66]
        print(f"    {w.get('direction')} {w.get('contribution'):+} | {d}")

    print_section(5, total, "Neuro-symbolic — does a correction layer beat neural?")
    summary = api.predictions.discover_prediction_rules(
        pid, prediction_config_id=cfg["id"], timeout=args.discover_timeout)
    accepted = summary.get("total_accepted") or 0
    print(f"  rounds={summary.get('rounds')}  accepted={accepted} "
          f"rejected={summary.get('total_rejected')}")
    if accepted:
        print(f"  The symbolic correction layer added value: {accepted} discovered rule(s) "
              "beat the neural backtest, held pending expert approval.")
    else:
        print("  No discovered correction rule beat the neural backtest — macro alone barely "
              "moves geopolitical risk (as expected; a news signal is the real driver).")

    print(f"\nDone. Platform {pid}. The platform chose the drivers and showed its working — an "
          "honest read on how little macro explains geopolitical risk.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Geopolitical risk (GPR) macro forecast — let the system pick the drivers")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="bundled macro panel CSV")
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    parser.add_argument("--autoregressive", choices=["full", "limited", "none"], default="none",
                        help="how much the model may use GPR's own history (default: none; GPR "
                             "is persistent so --autoregressive limited gives a persistence base)")
    parser.add_argument("--discover-timeout", type=float, default=1500.0,
                        help="seconds to wait for neuro-symbolic rule discovery")
    args = parser.parse_args()
    run_demo(run_geopol_forecast, args)


if __name__ == "__main__":
    main()
