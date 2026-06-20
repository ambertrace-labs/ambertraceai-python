"""GBP/USD — readable rules that beat the random walk (system picks the drivers).

The sterling companion to the FRED macro demos: don't hand-pick features. Give the
platform a BROAD, neutral macro panel and let it tell you which drivers explain the
GBP/USD exchange rate, with the readable WHEN->THEN rules to back it.

What's different here: the panel is pulled LIVE from the FRED connector, not a
bundled CSV. One ``datasets.fetch`` call merges ~18 monthly series into a single
date-keyed table:

  * sterling cross: EXUSUK (US$ per £ — this is GBP/USD, the target)
  * UK rates / activity: UK 10y + 3m rates, UK CPI, unemployment, industrial
    production, business confidence, the OECD UK leading indicator
  * euro area: euro 10y yield, euro HICP (the EUR/GBP linkage matters for cable)
  * US: FEDFUNDS, GS10, GS2, CPI, unemployment, industrial production, M2
  * commodities: WTI oil

Then, exactly like the other macro demos:
  1. Build a verified platform on the fetched panel.
  2. Run the SYMBOLIC-only forecaster on EXUSUK — induced WHEN->THEN driver rules,
     no neural network — and read its skill-vs-persistence and the rules.

Honest framing: the value is the EXPLANATION — which macro drivers the platform kept
and the readable rules over them — together with an honest walk-forward skill score.
On a monthly FX level a last-value baseline is hard to beat; the symbolic forecaster
reports its skill_vs_persistence so you can see exactly how much the rules add.

DATA: all series are FRED (US-government / OECD public data). Needs a free FRED API
key. Get one at https://fred.stlouisfed.org -> My Account -> API Keys, then put it
in examples/.env as:

    FRED_API_KEY=your_fred_key

The fetch is live, so the panel is always current.

    python gbpusd_macro_forecast.py                 # build + show which drivers the system chose
    python gbpusd_macro_forecast.py --standard      # skip the verified profile
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict

from _common import (
    build_ontology,
    build_platform,
    fred_api_key,
    print_dataset,
    print_section,
    run_demo,
    train_prediction_model,
)

TARGET = "EXUSUK"  # FRED: US$ to one UK£ — i.e. GBP/USD ("cable")
START_DATE = "1999-01-01"  # dense common window (euro-area series start 1999)

# A broad, deliberately NON-cherry-picked monthly macro panel, all on FRED.
PANEL = [
    TARGET,
    # --- UK ---
    "IRLTLT01GBM156N",   # UK 10-year government bond yield
    "IR3TIB01GBM156N",   # UK 3-month interbank rate
    "GBRCPIALLMINMEI",   # UK CPI, all items
    "LRHUTTTTGBM156S",   # UK unemployment rate
    "GBRPROINDMISMEI",   # UK industrial production
    "BSCICP02GBM460S",   # UK business confidence
    "GBRLOLITONOSTSAM",  # OECD composite leading indicator, UK
    # --- euro area (cable moves with EUR/GBP) ---
    "IRLTLT01EZM156N",   # euro-area 10-year yield
    "CP0000EZ19M086NEST",  # euro-area HICP
    # --- US ---
    "FEDFUNDS", "GS10", "GS2", "CPIAUCSL", "UNRATE", "INDPRO", "M2SL",
    # --- commodities ---
    "MCOILWTICO",        # WTI crude oil
]

DOMAIN_NAME = "GBP/USD explainable forecast (system feature selection)"
DOMAIN_DESCRIPTION = (
    "Forecast EXUSUK, the GBP/USD exchange rate (US dollars per pound sterling), one "
    "month ahead from a broad UK, euro-area and US macro panel: UK interest rates "
    "(IRLTLT01GBM156N, IR3TIB01GBM156N), UK inflation (GBRCPIALLMINMEI), UK labour "
    "(LRHUTTTTGBM156S), UK activity (GBRPROINDMISMEI, BSCICP02GBM460S, "
    "GBRLOLITONOSTSAM), euro-area rates and inflation (IRLTLT01EZM156N, "
    "CP0000EZ19M086NEST), US rates (FEDFUNDS, GS10, GS2), US inflation (CPIAUCSL), US "
    "labour (UNRATE), US activity (INDPRO), money (M2SL) and the oil price (MCOILWTICO). "
    "Let the data decide which drivers matter for sterling."
)

_SUFFIX_RE = re.compile(r"_(rollmean|rollstd|rollchg|rolldev|pctchg|lag|roc|chg|diff|zscore)")


def _aggregate_importance(feature_importance: list) -> list[tuple[str, float]]:
    """Sum engineered-feature importance back to base series (drop _lag_/_roc_/... suffixes)."""
    base: dict[str, float] = defaultdict(float)
    for x in feature_importance or []:
        name = x.get("feature") if isinstance(x, dict) else x[0]
        imp = (x.get("importance") if isinstance(x, dict) else x[1]) or 0
        base[_SUFFIX_RE.split(name)[0]] += imp
    return sorted(base.items(), key=lambda kv: -kv[1])


def run_gbpusd_forecast(api, args: argparse.Namespace) -> None:
    key = fred_api_key()
    if not key:
        print("ERROR: this demo fetches live from FRED. Set FRED_API_KEY in examples/.env.",
              file=sys.stderr)
        sys.exit(1)
    total = 4

    print_section(1, total, "Fetching the UK+euro+US macro panel live from FRED")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.fetch(
        domain_id=domain["id"], connector_type="fred",
        config={"series_ids": PANEL, "api_key": key, "start_date": args.start})
    print_dataset(dataset)
    print(f"  pulled {len(PANEL)} series from FRED into one dataset (target={TARGET})")

    print_section(2, total, "Building ontology + verified platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]
    # autoregressive="none": forbid leaning on EXUSUK's own lags/momentum, so the
    # model must EXPLAIN cable through the macro panel rather than soaking up the
    # autocorrelation. The symbolic forecaster is then a clean read of the drivers.
    cfg = api.predictions.create_config(
        pid, mode="timeseries", target_field=TARGET, time_index_field="date",
        horizon=args.horizon, frequency="monthly", model_type="gbt",
        autoregressive=args.autoregressive)
    cfg = train_prediction_model(api, pid, cfg["id"])

    print_section(3, total, "What the SYSTEM selected — neural feature importance")
    ar_note = ("drivers only — no EXUSUK own-history features"
               if args.autoregressive == "none" else args.autoregressive)
    print(f"  autoregressive={args.autoregressive} ({ar_note})")
    base = api.predictions.predict(pid, prediction_config_id=cfg["id"])
    ranking = _aggregate_importance(
        (base.get("explanation") or {}).get("feature_importance"))
    kept = [(b, i) for b, i in ranking if i > 0 and b != "date"]
    print(f"  the model kept {len(kept)} macro series with non-zero importance "
          "(aggregated by base series):")
    for b, imp in kept:
        print(f"    {b:18s} {imp:.4f}")

    print_section(4, total, "SYMBOLIC-only forecaster — induced WHEN-THEN driver rules")
    sf = api.predictions.symbolic_forecast(
        pid, prediction_config_id=cfg["id"], verified=not args.standard)
    why = sf.get("why") or []
    skill = sf.get("skill_vs_persistence")
    forecast = sf.get("forecast") or {}
    print(f"  {len(why)} driver rules induced; baseline={sf.get('baseline')} "
          f"forecast={forecast.get('value')}")
    print(f"  symbolic skill_vs_persistence={skill} "
          "(walk-forward backtest; +ve beats a last-value baseline)")
    # Full rule set, not a teaser — these are the model.
    for w in sorted(why, key=lambda x: -abs(x.get("contribution") or 0)):
        contribution = w.get("contribution") or 0.0
        print(f"    {w.get('direction')} {contribution:+.4f} | {w.get('driver')}")

    print(f"\n✓ Done. Platform {pid}. The platform chose the drivers and showed its "
          "working — explainable fit + readable rules, not a market-beating FX signal.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="GBP/USD explainable macro forecast — let the system pick the drivers")
    # add_common_args / add_verified_args supply --url, --api-key, -v, --standard, --tau.
    from _common import add_common_args, add_verified_args
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    parser.add_argument("--start", default=START_DATE,
                        help=f"FRED observation start date (default: {START_DATE})")
    parser.add_argument("--autoregressive", choices=["full", "limited", "none"], default="none",
                        help="how much the model may use EXUSUK's own history (default: none — "
                             "force it to explain via the macro panel)")
    args = parser.parse_args()
    run_demo(run_gbpusd_forecast, args)


if __name__ == "__main__":
    main()
