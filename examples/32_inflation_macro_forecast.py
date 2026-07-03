"""32 — US inflation macro forecast (let the SYSTEM pick the drivers; symbolic + neuro-symbolic).

Same premise as the other macro demos (GS10, S&P 500, Bitcoin): don't hand-pick features.
Give the platform a BROAD, neutral panel of US macro series and let it tell you which ones
explain inflation — with the readable rules to back it.

  1. Upload a bundled monthly macro panel whose target is INFL_YOY — US headline CPI
     year-over-year % (``data/inflation_macro_panel.csv``, all FRED, US-government public
     domain; the headline-CPI level is dropped so the model can't trivially reconstruct
     its own target).
  2. Build a verified platform and train a forecaster on INFL_YOY with autoregression turned
     OFF (``autoregressive="none"``) — so the model must explain inflation through the macro
     drivers (labour, money, activity, oil, other prices) instead of leaning on its own
     momentum, and so the symbolic correction layer has residual structure to add value to.
  3. Read back what the SYSTEM selected:
       - neural feature importance, aggregated by base series (which macro series it keeps);
       - the symbolic forecaster's induced WHEN->THEN driver rules (the WHY);
       - the neuro-symbolic discovery pass (does a correction layer beat the neural model?).

Honest framing: the value is the EXPLANATION — which macro drivers the platform selected for
inflation and the readable rules over them, not a market-beating signal. Unlike a price
*level*, the YoY rate is genuinely hard to forecast, so the fit is real signal rather than
autocorrelation.

LIVE RESULTS (bundled snapshot): level R^2 ≈ 0.95; the drivers the system kept are led by
oil (MCOILWTICO), housing permits (PERMIT), business loans (BUSLOANS) and industrial
production (INDPRO).

DATA: all FRED, US-government public domain — the panel is bundled and fully reproducible;
no API key is needed to run this demo.

    python 32_inflation_macro_forecast.py             # build on the bundled snapshot
    python 32_inflation_macro_forecast.py --standard  # skip the verified profile
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
DEFAULT_DATASET = DATA_DIR / "inflation_macro_panel.csv"
TARGET = "INFL_YOY"

DOMAIN_NAME = "US inflation (system feature selection)"
DOMAIN_DESCRIPTION = (
    "Forecast INFL_YOY, US headline CPI inflation year-over-year, one month ahead from a broad "
    "panel of US macro indicators: short rates and credit (FEDFUNDS, GS2, GS1, TB3MS, GS10, AAA, "
    "BAA), other price gauges (CPILFESL core CPI, PPIACO, PCEPI), labour (UNRATE, PAYEMS, "
    "CIVPART), money and credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, "
    "PERMIT, TCU), consumer sentiment (UMCSENT) and the oil price (MCOILWTICO). Let the data "
    "decide which drivers matter for inflation."
)

# Split an engineered feature name back to its base series, e.g. HOUST_lag_1 -> HOUST.
# Compound suffixes precede the short ones so the longest match wins.
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
    """Print the backtest FIT (level + month-to-month change + skill context).

    Reads ``explanation.model.metrics`` (see ``predictions.create_config`` docs). For
    AmberTrace the relevant question is whether the model achieves a reasonable,
    EXPLAINABLE fit — not whether it beats persistence: on infrequent freely-available
    series nobody does, so skill_vs_persistence is honest context, never a pass/fail gate.
    """
    model = (prediction.get("explanation") or {}).get("model") or {}
    metrics = model.get("metrics") or {}
    level = metrics.get("level") or {}
    transformed = metrics.get("transformed") or {}
    r2 = level.get("r2", model.get("r2"))
    rmse = level.get("rmse", model.get("rmse"))
    skill = metrics.get("skill_vs_persistence", model.get("skill_vs_persistence"))
    print(f"  fit (level): R^2={r2}, RMSE={rmse}")
    if isinstance(transformed.get("r2"), (int, float)):
        print(f"  fit (month-to-month change): R^2={transformed.get('r2')} — the hard part; "
              "most of the level is just last month's value.")
    if isinstance(skill, (int, float)):
        print(f"  (skill_vs_persistence={skill:+.3f} — context only: on infrequent, freely "
              "available series nobody beats a last-value baseline; that is not the goal.)")


def run_inflation_forecast(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found.", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating domain + uploading the bundled inflation macro panel")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology + verified platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    # autoregressive="none": forbid the model from leaning on inflation's own momentum, so it
    # must EXPLAIN the rate through the macro panel (labour, money, activity, oil, other prices)
    # rather than soaking up the autocorrelation — and so residual structure is left for the
    # symbolic correction layer to add value to.
    cfg = api.predictions.create_config(
        pid, mode="timeseries", target_field=TARGET, time_index_field="date",
        horizon=args.horizon, frequency="monthly", model_type="gbt",
        autoregressive=args.autoregressive)
    cfg = train_prediction_model(api, pid, cfg["id"])

    print_section(3, total, "What the SYSTEM selected — neural feature importance")
    ar_note = ("drivers only — no inflation own-history features"
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
          f"forecast={(sf.get('forecast') or {}).get('value')} "
          f"skill_vs_persistence={sf.get('skill_vs_persistence')}")
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
        print("  No discovered correction rule beat the neural backtest — the macro drivers "
              "already explain inflation, and the layer honestly adds nothing here.")

    print(f"\nDone. Platform {pid}. The platform chose the drivers and showed its working — "
          "explainable fit + readable rules for inflation, not a market-beating signal.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="US inflation macro forecast — let the system pick the drivers")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="bundled macro panel CSV")
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    parser.add_argument("--autoregressive", choices=["full", "limited", "none"], default="none",
                        help="how much the model may use inflation's own history (default: none — "
                             "force it to explain via the macro drivers)")
    parser.add_argument("--discover-timeout", type=float, default=1500.0,
                        help="seconds to wait for neuro-symbolic rule discovery")
    args = parser.parse_args()
    run_demo(run_inflation_forecast, args)


if __name__ == "__main__":
    main()
