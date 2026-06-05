"""16 — Environmental Monitoring Time-Series Forecast.

Exercises AmbertraceAI as a forecasting back-end via the prediction API:
  1. Create domain + upload environmental monitoring data
  2. Build ontology + platform (symbolic rules)
  3. Create a PredictionConfig (target=measurement_value, time=reading_date)
  4. Train the model
  5. Run predictions for several scenarios and inspect intervals + drivers

Dataset: environmental_monitoring.csv (60 readings, 16 facilities).
Creates resources on your account. Run with --help for options.

    python 15_timeseries_forecast.py
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
    prediction_values,
    print_dataset,
    print_ontology,
    print_prediction_explanation,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "environmental_monitoring.csv"

DOMAIN_NAME = "Environmental Monitoring Forecasting"
DOMAIN_DESCRIPTION = (
    "Environmental pollution monitoring and compliance forecasting. "
    "Facilities are monitored for pollutant levels (nitrogen dioxide, "
    "particulate matter, sulphur dioxide, carbon monoxide, benzene, etc.) "
    "with readings taken over time. Each reading has a measurement value, "
    "a regulatory limit, and a permit limit. The goal is to forecast "
    "future measurement values based on historical trends, facility type, "
    "pollutant characteristics, and seasonal patterns. Facilities in "
    "different zone classifications (urban, rural, industrial) show "
    "different pollution patterns."
)

PREDICTION_SCENARIOS = [
    {
        "name": "Baseline forecast",
        "description": "Default prediction with no overrides — uses latest data trends",
        "input": {},
    },
    {
        "name": "High-pollution facility",
        "description": "Chemical plant in industrial zone — expect higher forecast",
        "input": {"facility_type": "chemical_plant", "zone_classification": "industrial"},
    },
    {
        "name": "Clean facility",
        "description": "Renewable energy in rural zone — expect lower forecast",
        "input": {
            "facility_type": "renewable_energy",
            "zone_classification": "rural_agricultural",
        },
    },
    {
        "name": "Near-limit scenario",
        "description": "Reading near regulatory limit — rules should flag",
        "input": {"measurement_value": 39.5, "regulatory_limit": 40.0},
    },
    {
        "name": "Over-limit scenario",
        "description": "Reading exceeds limit — rules should trigger corrective action",
        "input": {"measurement_value": 45.0, "regulatory_limit": 40.0},
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
    print(f"  Predicted value: {value:.2f}")
    print(f"  Interval: [{lower:.2f}, {upper:.2f}]  (width {width:.2f})")
    print_prediction_explanation(prediction)
    print("=" * 70)
    return {
        "name": scenario["name"],
        "value": value,
        "lower": lower,
        "upper": upper,
        "width": width,
    }


def run_timeseries_experiment(api, args: argparse.Namespace) -> None:
    total = 7

    print_section(1, total, "Creating environmental forecasting domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading environmental monitoring data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(4, total, "Building platform")
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(5, total, "Creating prediction config")
    config = api.predictions.create_config(
        platform["id"],
        target_field="measurement_value",
        time_index_field="reading_date",
        horizon=1,
        frequency="monthly",
        model_type="gbt",
    )
    print(f"  Config {config['id']}: target={config.get('target_field')}, "
          f"model={config.get('model_type')} ({config.get('status')})")

    print_section(6, total, "Training prediction model")
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Training complete: status={config.get('status')}")

    print_section(7, total, "Running prediction scenarios")
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
        widths = [r["width"] for r in results]
        print(f"\n  Predictions: {len(results)}/{len(PREDICTION_SCENARIOS)}")
        print(f"  Value range: {min(values):.2f} — {max(values):.2f}")
        print(f"  Avg interval width: {sum(widths) / len(widths):.2f}")
        for r in results:
            print(f"    {r['name']:30s}  value={r['value']:8.2f}  "
                  f"interval=[{r['lower']:7.2f}, {r['upper']:7.2f}]")

    history = api.predictions.list_predictions(platform["id"])
    print(f"\n  Stored forecasts: {len(history)}")
    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Environmental Monitoring — Time-Series Forecasting demo",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_timeseries_experiment, args)


if __name__ == "__main__":
    main()
