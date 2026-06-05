"""21 — Bitcoin Forecast.

Daily BTC-USD price forecasting via the Coinbase connector. Ingests daily
close prices (BTC-USD, with ETH-USD as a co-moving covariate) through the
built-in coinbase connector — no API key needed — then builds a platform and
forecasts the next BTC-USD close:
  1. Create domain
  2. Fetch BTC-USD + ETH-USD from the coinbase connector
  3. Build ontology + platform
  4. Create a PredictionConfig (target=BTC-USD, time=date, feature=ETH-USD)
  5. Train and forecast under a few covariate scenarios

Caveat: this forecasts the raw price level of a strongly-trending asset, which
is a deliberately hard case for tree models (they can't extrapolate beyond the
training range).

Creates resources on your account. Run with --help for options.

    python 21_bitcoin_forecast.py
"""

from __future__ import annotations

import argparse
from typing import Any

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    fetch_dataset,
    prediction_values,
    print_dataset,
    print_ontology,
    print_prediction_explanation,
    print_section,
    run_demo,
    train_prediction_model,
)

DOMAIN_NAME = "Bitcoin Price Forecasting"
DOMAIN_DESCRIPTION = (
    "Daily cryptocurrency price forecasting. Tracks Coinbase close prices for "
    "major trading pairs. BTC-USD is the headline asset; ETH-USD tends to "
    "co-move with it. The goal is to forecast the next BTC-USD close from recent "
    "price history and the co-moving ETH-USD series."
)
PRODUCT_IDS = ["BTC-USD", "ETH-USD"]

PREDICTION_SCENARIOS = [
    {"name": "Baseline", "description": "Latest trend, no overrides", "input": {}},
    {"name": "ETH rally", "description": "ETH-USD set high — crypto risk-on",
     "input": {"ETH-USD": 4000}},
    {"name": "ETH crash", "description": "ETH-USD set low — crypto risk-off",
     "input": {"ETH-USD": 1500}},
]


def print_scenario(scenario: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    value, lower, upper = prediction_values(prediction)
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"  {scenario['description']}")
    if scenario["input"]:
        print(f"  Inputs: {scenario['input']}")
    print("-" * 70)
    print(f"  Forecast BTC-USD close: ${value:,.0f}")
    print(f"  Interval: [${lower:,.0f}, ${upper:,.0f}]  (width ${upper - lower:,.0f})")
    print_prediction_explanation(prediction)
    print("=" * 70)
    return {"name": scenario["name"], "value": value, "lower": lower, "upper": upper}


def run_bitcoin_forecast(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Creating Bitcoin forecasting domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Fetching Coinbase close prices")
    dataset = fetch_dataset(api, domain["id"], "coinbase", {"product_ids": PRODUCT_IDS})
    print_dataset(dataset)

    print_section(3, total, "Building ontology")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(4, total, "Building platform")
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(5, total, "Creating + training prediction model (target=BTC-USD)")
    config = api.predictions.create_config(
        platform["id"],
        target_field="BTC-USD",
        time_index_field="date",
        horizon=1,
        frequency="daily",
        model_type="gbt",
        feature_fields=["ETH-USD"],
    )
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Config {config['id']}: status={config.get('status')}")

    print_section(6, total, "Forecasting under covariate scenarios")
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
        print(f"\n  Forecast range: ${min(values):,.0f} — ${max(values):,.0f}  "
              f"(spread ${max(values) - min(values):,.0f})")
        print("  Note: tree models can't extrapolate beyond the training price range; "
              "compare the forecast to the latest BTC-USD close.")
    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Bitcoin — Coinbase price forecasting demo")
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_bitcoin_forecast, args)


if __name__ == "__main__":
    main()
