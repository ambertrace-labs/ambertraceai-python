"""22 — S&P 500 macro forecast (let the SYSTEM pick the drivers; symbolic + neuro-symbolic).

The premise: don't hand-pick features. Give the platform a BROAD, neutral panel of US
macro series and let it tell you which ones move the S&P 500 — with the rules to back it.

  1. Live-fetch a 25-series monthly macro panel + the S&P 500 from the ``fred`` connector
     (rates, inflation, labour, money/credit, activity, sentiment, oil) — chosen for
     breadth, NOT for equity relevance.
  2. Build a verified platform and train a forecaster on SP500 with autoregression turned
     OFF (``autoregressive="none"``) — so the model must explain the index through the
     macro drivers instead of leaning on its own recent value, and so the symbolic
     correction layer has residual structure to add value to.
  3. Read back what the SYSTEM selected:
       - neural feature importance, aggregated by base series (which macro series it keeps);
       - the symbolic forecaster's induced WHEN->THEN driver rules (the WHY);
       - the neuro-symbolic discovery pass (does a correction layer beat the neural model?).

Honest framing: the value is the EXPLANATION — which macro drivers the platform selected,
the readable rules over them, and whether the symbolic layer adds value to the neural model.
It is not about beating a persistence baseline (on a monthly level forecast that is trivial
autocorrelation, which is exactly why we turn autoregression off). Fit is read as level-space
R^2; skill_vs_persistence is shown only as context. With only ~10 years of S&P 500 history on
FRED (~118 monthly rows), treat the selection as suggestive, not definitive.

DATA / LICENSING: the S&P 500 series on FRED is S&P Dow Jones Indices copyrighted and
**not redistributable**, so this demo is LIVE-FETCH only — it ships the code, never the
data. It needs a free FRED key (``FRED_API_KEY`` in examples/.env). FRED's macro series
are US-government public domain; the S&P 500 values are not, so do not redistribute any
panel this fetches.

    python 22_sp500_macro_forecast.py             # fetch live, build, show which drivers the system chose
    python 22_sp500_macro_forecast.py --standard  # skip the verified profile
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from typing import Any

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    fred_api_key,
    print_dataset,
    print_section,
    run_demo,
    train_prediction_model,
)

# Broad, neutral monthly macro panel (target first). Chosen for breadth across categories,
# NOT for equity predictiveness — the point is to let the platform select.
TARGET = "SP500"
FRED_PANEL = [
    TARGET,
    "FEDFUNDS", "GS10", "GS2", "GS1", "TB3MS", "AAA", "BAA",   # rates / credit
    "CPIAUCSL", "CPILFESL", "PPIACO", "PCEPI",                  # inflation
    "UNRATE", "PAYEMS", "CIVPART",                             # labour
    "M2SL", "M1SL", "TOTALSL", "BUSLOANS",                     # money / credit
    "INDPRO", "RSAFS", "HOUST", "PERMIT", "TCU",               # activity
    "UMCSENT", "MCOILWTICO",                                   # sentiment / oil
]

DOMAIN_NAME = "S&P 500 macro (system feature selection)"
DOMAIN_DESCRIPTION = (
    "Forecast SP500, the S&P 500 equity index, one month ahead from a broad panel of US "
    "macro indicators: interest rates (FEDFUNDS, GS10, GS2, GS1, TB3MS, AAA, BAA), inflation "
    "(CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour (UNRATE, PAYEMS, CIVPART), money and credit "
    "(M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), consumer "
    "sentiment (UMCSENT) and the oil price (MCOILWTICO). Let the data decide which drivers "
    "matter for the index."
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


def _wait_dataset_ready(api, dataset_id: int, *, timeout: int = 300, poll: int = 4) -> dict:
    """Poll a connector-fetched dataset until it reports ``ready`` (fetch is async)."""
    import time
    deadline = time.monotonic() + timeout
    while True:
        ds = api.datasets.get(dataset_id)
        status = ds.get("status", "")
        if status in ("ready", "active", "completed"):
            return ds
        if status in ("failed", "error"):
            raise RuntimeError(f"Dataset {dataset_id} fetch failed (status: {status})")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"Dataset {dataset_id} not ready within {timeout}s (status: {status})")
        time.sleep(poll)


def run_sp500_forecast(api, args: argparse.Namespace) -> None:
    key = fred_api_key()
    if not key:
        print("ERROR: this demo is live-fetch only (the S&P 500 series is not "
              "redistributable) and needs a FRED API key. Set FRED_API_KEY in examples/.env "
              "(free at https://fred.stlouisfed.org).", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, f"Live-fetching the {len(FRED_PANEL)}-series FRED macro panel + S&P 500")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    ds = api.datasets.fetch(
        domain_id=domain["id"], connector_type="fred",
        config={"series_ids": FRED_PANEL, "api_key": key, "frequency": "monthly"})
    dataset = _wait_dataset_ready(api, ds["id"])
    print_dataset(dataset)
    print(f"  pulled {len(FRED_PANEL)} series from FRED into one dataset (target={TARGET})")

    print_section(2, total, "Building ontology + verified platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    # autoregressive="none": forbid leaning on SP500's own lags/momentum, so the model must
    # EXPLAIN the index through the macro panel rather than soaking up the autocorrelation —
    # and so residual structure is left for the symbolic correction layer to add value to.
    cfg = api.predictions.create_config(
        pid, mode="timeseries", target_field=TARGET, time_index_field="date",
        horizon=args.horizon, frequency="monthly", model_type="gbt",
        autoregressive=args.autoregressive)
    cfg = train_prediction_model(api, pid, cfg["id"])

    print_section(3, total, "What the SYSTEM selected — neural feature importance")
    ar_note = ("drivers only — no SP500 own-history features"
               if args.autoregressive == "none" else args.autoregressive)
    print(f"  autoregressive={args.autoregressive} ({ar_note})")
    base = api.predictions.predict(pid, prediction_config_id=cfg["id"])
    _print_fit(base)
    ranking = _aggregate_importance((base.get("explanation") or {}).get("feature_importance"))
    kept = [(b, i) for b, i in ranking if i > 0 and b != "date"]
    print(f"  the model kept {len(kept)} of {len(FRED_PANEL) - 1} candidate series "
          "(importance by base series):")
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
              "beat the neural backtest and are held pending expert approval.")
    else:
        print("  No discovered correction rule beat the neural backtest on this run.")
    print("  NOTE: discovery is A/B-tested on a short (~118-row) history and is variable "
          "run-to-run — on this panel it accepts 0-1 rules. Treat 'neuro-symbolic beats "
          "neural' as marginal here, not a headline; the robust value is the explanation.")

    print(f"\nDone. Platform {pid}. The platform chose the drivers and showed its working — "
          "explainable fit + readable rules, not a market-beating signal.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="S&P 500 macro forecast — let the system pick the drivers")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    parser.add_argument("--autoregressive", choices=["full", "limited", "none"], default="none",
                        help="how much the model may use SP500's own history (default: none — "
                             "force it to explain via the macro drivers)")
    parser.add_argument("--discover-timeout", type=float, default=1500.0,
                        help="seconds to wait for neuro-symbolic rule discovery")
    args = parser.parse_args()
    run_demo(run_sp500_forecast, args)


if __name__ == "__main__":
    main()
