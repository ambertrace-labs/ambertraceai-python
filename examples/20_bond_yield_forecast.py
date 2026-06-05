"""20 — Bond Yield Forecast.

Macroeconomic forecasting of the US 10-year Treasury yield (GS10) from monthly
macro drivers using the prediction API:
  1. Create domain + upload FRED economic data (or fetch via FRED connector)
  2. Build ontology + platform (symbolic rules over macro regimes)
  3. Create a PredictionConfig (target=GS10, time=date)
  4. Train the model
  5. Forecast the yield under several macro scenarios

Dataset: fred_economic_data.csv (monthly, 2015 onwards). Columns: GS10
(10y Treasury yield, the target), FEDFUNDS, CPIAUCSL, DCOILWTICO (WTI oil),
UNRATE, M2SL.

Creates resources on your account. Run with --help for options.

    python 20_bond_yield_forecast.py
    python 20_bond_yield_forecast.py --dataset data/fred_economic_data.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    fetch_dataset,
    fred_api_key,
    prediction_values,
    print_dataset,
    print_ontology,
    print_prediction_explanation,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "fred_economic_data.csv"

DOMAIN_NAME = "Bond Yield Macro Forecasting"
DOMAIN_DESCRIPTION = (
    "Macroeconomic forecasting of the US 10-year Treasury yield (GS10). "
    "Each monthly observation includes the federal funds rate (FEDFUNDS), "
    "the consumer price index (CPIAUCSL), the WTI crude oil price "
    "(DCOILWTICO), the unemployment rate (UNRATE), and the M2 money supply "
    "(M2SL). The 10-year yield generally rises with the policy rate and "
    "inflation expectations and falls when growth weakens or investors seek "
    "safety. The goal is to forecast GS10 from these macro drivers."
)

FRED_SERIES = ["GS10", "FEDFUNDS", "CPIAUCSL", "DCOILWTICO", "UNRATE", "M2SL"]

PREDICTION_SCENARIOS = [
    {"name": "Baseline", "description": "No overrides — latest macro trends", "input": {}},
    {
        "name": "High Fed funds",
        "description": "Aggressive rate hikes — expect higher yield",
        "input": {"FEDFUNDS": 5.5},
    },
    {
        "name": "Low Fed funds",
        "description": "Rate cuts to the floor — expect lower yield",
        "input": {"FEDFUNDS": 0.25},
    },
    {
        "name": "High inflation",
        "description": "Inflation spike — expect higher yield",
        "input": {"CPIAUCSL": 320.0},
    },
    {
        "name": "Low oil",
        "description": "Oil price collapse — disinflationary",
        "input": {"DCOILWTICO": 25.0},
    },
    {
        "name": "Stagflation",
        "description": "High inflation with high unemployment",
        "input": {"CPIAUCSL": 320.0, "UNRATE": 8.0, "FEDFUNDS": 5.0},
    },
    {
        "name": "Growth",
        "description": "Strong economy, low unemployment",
        "input": {"UNRATE": 3.5, "FEDFUNDS": 3.0, "DCOILWTICO": 80.0},
    },
    {
        "name": "Crisis",
        "description": "Flight to safety — recession shock",
        "input": {"UNRATE": 10.0, "FEDFUNDS": 0.25, "DCOILWTICO": 30.0},
    },
]


def print_scenario(scenario: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    value, lower, upper = prediction_values(prediction)
    width = upper - lower
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"  {scenario['description']}")
    if scenario["input"]:
        print(f"  Inputs: {scenario['input']}")
    print("-" * 70)
    print(f"  Predicted 10y yield: {value:.2f}%")
    print(f"  Interval: [{lower:.2f}%, {upper:.2f}%]  (width {width:.2f} pp)")
    print_prediction_explanation(prediction)
    print("=" * 70)
    return {
        "name": scenario["name"], "value": value, "lower": lower, "upper": upper, "width": width,
    }


def run_bond_yield_forecast(api, args: argparse.Namespace) -> None:
    total = 7

    print_section(1, total, "Creating bond yield forecasting domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    key = fred_api_key()
    if key:
        print_section(2, total, "Fetching FRED data via connector")
        dataset = fetch_dataset(
            api, domain["id"], "fred", {"series_ids": FRED_SERIES, "api_key": key},
        )
    else:
        print_section(2, total, "Uploading FRED CSV (set FRED_API_KEY for live connector)")
        dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(4, total, "Building platform")
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(5, total, "Creating prediction config (target=GS10)")
    config = api.predictions.create_config(
        platform["id"],
        target_field="GS10",
        time_index_field="date",
        horizon=1,
        frequency="monthly",
        model_type="gbt",
    )
    print(f"  Config {config['id']}: target={config.get('target_field')}, "
          f"model={config.get('model_type')} ({config.get('status')})")

    print_section(6, total, "Training prediction model")
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Training complete: status={config.get('status')}")

    print_section(7, total, "Running macro scenarios")
    results = []
    for scenario in PREDICTION_SCENARIOS:
        try:
            prediction = api.predictions.predict(
                platform["id"],
                prediction_config_id=config["id"],
                feature_overrides=scenario["input"] or None,
            )
            results.append(print_scenario(scenario, prediction))
        except AmbertraceError as exc:
            print(f"\n  SCENARIO '{scenario['name']}' FAILED: {exc}")

    if results:
        values = [r["value"] for r in results]
        spread = max(values) - min(values)
        unique_values = len({round(v, 3) for v in values})
        print(f"\n  Predictions: {len(results)}/{len(PREDICTION_SCENARIOS)}")
        print(f"  Yield range: {min(values):.2f}% — {max(values):.2f}%  (spread {spread:.2f} pp)")
        print(f"  Unique predicted values: {unique_values}/{len(results)}")
        if unique_values == 1:
            print("  WARNING: All scenarios returned the same value — overrides not applied")
        else:
            print("  OK: Forecast responds to macro inputs")
        for r in results:
            print(f"    {r['name']:18s}  yield={r['value']:6.2f}%  "
                  f"interval=[{r['lower']:6.2f}%, {r['upper']:6.2f}%]")

    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Bond Yield — Macroeconomic Forecasting demo",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_bond_yield_forecast, args)


if __name__ == "__main__":
    main()
