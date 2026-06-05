"""22 — Equity Index Forecast.

Daily SPY forecasting via the Yahoo Finance connector. Ingests daily close
prices (SPY, with QQQ as a co-moving covariate) through the built-in yahoo
connector — no API key needed — then builds a platform and forecasts the next
SPY close:
  1. Create domain
  2. Fetch SPY + QQQ from the yahoo connector
  3. Build ontology + platform
  4. Create a PredictionConfig (target=SPY, time=date, feature=QQQ)
  5. Train and forecast under a few covariate scenarios

Same caveat as the Bitcoin demo: this forecasts a raw, trending price level —
a hard case for tree models.

Creates resources on your account. Run with --help for options.

    python 22_equity_forecast.py
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

DOMAIN_NAME = "Equity Index Forecasting"
DOMAIN_DESCRIPTION = (
    "Daily US equity index forecasting. Tracks Yahoo Finance close prices for "
    "the S&P 500 ETF (SPY) and the Nasdaq-100 ETF (QQQ), which move together. "
    "The goal is to forecast the next SPY close from recent price history and "
    "the co-moving QQQ series."
)
SYMBOLS = ["SPY", "QQQ"]

PREDICTION_SCENARIOS = [
    {"name": "Baseline", "description": "Latest trend, no overrides", "input": {}},
    {"name": "Tech rally", "description": "QQQ set high — tech-led risk-on",
     "input": {"QQQ": 620}},
    {"name": "Tech selloff", "description": "QQQ set low — tech-led risk-off",
     "input": {"QQQ": 420}},
]


def print_scenario(scenario: dict[str, Any], prediction: dict[str, Any]) -> dict[str, Any]:
    value, lower, upper = prediction_values(prediction)
    print(f"\n{'=' * 70}")
    print(f"SCENARIO: {scenario['name']}")
    print(f"  {scenario['description']}")
    if scenario["input"]:
        print(f"  Inputs: {scenario['input']}")
    print("-" * 70)
    print(f"  Forecast SPY close: ${value:,.2f}")
    print(f"  Interval: [${lower:,.2f}, ${upper:,.2f}]  (width ${upper - lower:,.2f})")
    print_prediction_explanation(prediction)
    print("=" * 70)
    return {"name": scenario["name"], "value": value, "lower": lower, "upper": upper}


def run_equity_forecast(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Creating equity forecasting domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Fetching Yahoo Finance close prices")
    dataset = fetch_dataset(api, domain["id"], "yahoo", {"symbols": SYMBOLS})
    print_dataset(dataset)

    print_section(3, total, "Building ontology")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(4, total, "Building platform")
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(5, total, "Creating + training prediction model (target=SPY)")
    config = api.predictions.create_config(
        platform["id"],
        target_field="SPY",
        time_index_field="date",
        horizon=1,
        frequency="daily",
        model_type="gbt",
        feature_fields=["QQQ"],
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
        print(f"\n  Forecast range: ${min(values):,.2f} — ${max(values):,.2f}  "
              f"(spread ${max(values) - min(values):,.2f})")
        print("  Note: compare the forecast to the latest SPY close — tree models "
              "can't extrapolate beyond the training price range.")
    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Equity index — Yahoo Finance forecasting demo")
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_equity_forecast, args)


if __name__ == "__main__":
    main()
