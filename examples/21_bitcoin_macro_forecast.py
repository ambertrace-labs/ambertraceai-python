"""21 — Bitcoin explainable macro-panel forecast (let the SYSTEM pick the drivers).

Same premise as the other macro demos (GS10, GBP/USD, S&P 500): don't hand-pick
features. Give the platform a BROAD panel of crypto + macro series and let it tell
you which ones explain Bitcoin — with the readable rules to back it.

  1. Upload a bundled monthly panel: BTC_USD + ETH_USD (Coinbase close prices,
     May 2016 - present) alongside 25 US macro series from FRED (rates, inflation,
     labour, money/credit, activity, sentiment, oil).
  2. Build a verified platform and train a forecaster on BTC_USD with autoregression
     turned OFF (``autoregressive="none"``) — so the model must explain Bitcoin
     through the crypto + macro panel instead of leaning on its own recent price.
  3. Read back what the SYSTEM selected:
       - neural feature importance, aggregated by base series (which drivers it keeps);
       - the symbolic forecaster's induced WHEN->THEN driver rules (the WHY);
       - the neuro-symbolic discovery pass (does a correction layer beat neural?).

Honest framing: the value is the EXPLANATION — which crypto and macro drivers the
platform kept and the readable rules over them — not beating persistence. On monthly
data nobody beats "next month ≈ this month" (if they did they'd be rich), which is
exactly why we turn autoregression off. What matters is the fit and the WHY.

DATA: BTC-USD and ETH-USD prices are from the Coinbase exchange API (free, no
licensing restriction); FRED macro series are US-government public domain. The bundled
CSV (``data/btc_macro_panel.csv``) is a point-in-time snapshot — pass ``--refresh`` to
build on a fresh panel pulled LIVE and merged from the ``coinbase`` + ``fred``
connectors instead (the refresh path needs a free FRED key, ``FRED_API_KEY`` in
examples/.env).

    python 21_bitcoin_macro_forecast.py             # build on the bundled snapshot
    python 21_bitcoin_macro_forecast.py --refresh   # fetch the panel live and build on that
    python 21_bitcoin_macro_forecast.py --standard  # skip the verified profile
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
    fred_api_key,
    print_dataset,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "btc_macro_panel.csv"
TARGET = "BTC_USD"

# Crypto products + a broad, deliberately NON-cherry-picked monthly macro panel.
# Used only with --refresh, to pull a fresh panel live from the connectors.
CRYPTO_PRODUCTS = ["BTC-USD", "ETH-USD"]
FRED_SERIES = [
    "FEDFUNDS", "GS10", "GS2", "GS1", "TB3MS", "AAA", "BAA",   # rates / credit
    "CPIAUCSL", "CPILFESL", "PPIACO", "PCEPI",                  # inflation
    "UNRATE", "PAYEMS", "CIVPART",                             # labour
    "M2SL", "M1SL", "TOTALSL", "BUSLOANS",                     # money / credit
    "INDPRO", "RSAFS", "HOUST", "PERMIT", "TCU",               # activity
    "UMCSENT", "MCOILWTICO",                                   # sentiment / oil
]

DOMAIN_NAME = "Bitcoin explainable forecast (system feature selection)"
DOMAIN_DESCRIPTION = (
    "Forecast BTC_USD, the Bitcoin price, one month ahead from a broad panel of crypto "
    "and US macro indicators: ETH_USD (Coinbase), interest rates (FEDFUNDS, GS10, GS2, "
    "GS1, TB3MS, AAA, BAA), inflation (CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour "
    "(UNRATE, PAYEMS, CIVPART), money and credit (M2SL, M1SL, TOTALSL, BUSLOANS), "
    "activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), consumer sentiment (UMCSENT) and "
    "the oil price (MCOILWTICO). Let the data decide which drivers matter for Bitcoin."
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


def run_bitcoin_forecast(api, args: argparse.Namespace) -> None:
    total = 5

    if args.refresh:
        key = fred_api_key()
        if not key:
            print("ERROR: --refresh pulls live from FRED and needs a key. Set FRED_API_KEY "
                  "in examples/.env (free at https://fred.stlouisfed.org).", file=sys.stderr)
            sys.exit(1)
        print_section(1, total, "Fetching BTC + ETH (coinbase) and the macro panel (fred) live")
        domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
        # fetch_multi merges the two connectors into ONE date-aligned monthly panel.
        # Each connector namespaces its columns (e.g. coinbase.BTC-USD, fred.GS10), so the
        # target is the namespaced BTC column on this path.
        ds = api.datasets.fetch_multi(
            domain_id=domain["id"],
            sources=[
                {"connector_type": "coinbase", "config": {"product_ids": CRYPTO_PRODUCTS}},
                {"connector_type": "fred", "config": {"series_ids": FRED_SERIES, "api_key": key}},
            ],
            join_on="date", frequency="monthly", aggregation="last")
        dataset = _wait_dataset_ready(api, ds["id"])
        target = "coinbase.BTC-USD"
    else:
        if not args.dataset.exists():
            print(f"ERROR: {args.dataset} not found. Run with --refresh to fetch live.",
                  file=sys.stderr)
            sys.exit(1)
        print_section(1, total, "Creating domain + uploading the bundled BTC + macro panel")
        domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
        dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
        target = TARGET
    print_dataset(dataset)

    print_section(2, total, "Building ontology + verified platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    # autoregressive="none": forbid leaning on the BTC target's own lags/momentum, so the
    # model must EXPLAIN Bitcoin through the crypto + macro panel rather than soaking up the
    # autocorrelation — and so residual structure is left for the symbolic correction layer.
    cfg = api.predictions.create_config(
        pid, mode="timeseries", target_field=target, time_index_field="date",
        horizon=args.horizon, frequency="monthly", model_type="gbt",
        autoregressive=args.autoregressive)
    cfg = train_prediction_model(api, pid, cfg["id"])

    print_section(3, total, "What the SYSTEM selected — neural feature importance")
    ar_note = ("drivers only — no BTC own-history features"
               if args.autoregressive == "none" else args.autoregressive)
    print(f"  autoregressive={args.autoregressive} ({ar_note})")
    base = api.predictions.predict(pid, prediction_config_id=cfg["id"])
    _print_fit(base)
    ranking = _aggregate_importance((base.get("explanation") or {}).get("feature_importance"))
    kept = [(b, i) for b, i in ranking if i > 0 and b != "date"]
    print(f"  the model kept {len(kept)} drivers with non-zero importance "
          "(aggregated by base series):")
    for b, imp in kept:
        print(f"    {b:18s} {imp:.4f}")

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
        print("  No discovered correction rule beat the neural backtest — the crypto + macro "
              "drivers already explain BTC, and the layer honestly adds nothing here.")

    print(f"\nDone. Platform {pid}. The platform chose the drivers and showed its working — "
          "explainable fit + readable rules, not a trading signal.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bitcoin explainable macro forecast — let the system pick the drivers")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="bundled panel CSV (ignored with --refresh)")
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    parser.add_argument("--autoregressive", choices=["full", "limited", "none"], default="none",
                        help="how much the model may use BTC's own history (default: none — "
                             "force it to explain via the crypto + macro panel)")
    parser.add_argument("--discover-timeout", type=float, default=1500.0,
                        help="seconds to wait for neuro-symbolic rule discovery")
    parser.add_argument("--refresh", action="store_true",
                        help="fetch the panel live from coinbase + fred (merged) instead of "
                             "the bundled CSV (needs FRED_API_KEY in examples/.env)")
    args = parser.parse_args()
    run_demo(run_bitcoin_forecast, args)


if __name__ == "__main__":
    main()
