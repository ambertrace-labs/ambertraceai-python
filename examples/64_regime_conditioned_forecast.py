"""64 -- Regime-conditioned forecast via composition.

Demonstrates ``regime_platform_id`` on PredictionConfig: the prediction
config references a separately-built Decisions platform that classifies
macro regimes (see example 61). At build time the panel is batch-classified
and one-hot regime dummies are injected as features; the symbolic forecaster
then learns regime-conditional rules. At forecast time a live classify of
the current observation produces a ``regime_provenance`` block on the
payload (label + proof certificate from the Decisions platform).

    python 64_regime_conditioned_forecast.py

Prerequisites:
- A built Decisions platform that classifies regimes (e.g. via example 61).
  Pass its ID with ``--regime-platform-id``.
"""

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    run_demo,
    setup_forecast_platform,
)

EXAMPLE_DATASET = str(Path(__file__).resolve().parent / "data" / "fred_economic_data.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regime-conditioned forecast example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    parser.add_argument(
        "--regime-platform-id", type=int, required=True,
        help="ID of a built Decisions platform that classifies regimes")
    add_common_args(parser)
    return parser.parse_args()


def run(api, args: argparse.Namespace) -> None:

    # --- Setup: domain + platform + data ---
    platform_id = setup_forecast_platform(
        api,
        name="regime_forecast_demo",
        description="Regime-conditioned forecast of the US 10-year Treasury yield (GS10) from monthly FRED macro drivers.",
        dataset_path=args.dataset,
    )

    # --- Create prediction config with regime conditioning ---
    config = api.predictions.create_config(
        platform_id,
        target_field="GS10",
        time_index_field="date",
        frequency="monthly",
        regime_platform_id=args.regime_platform_id,
    )
    print(f"Created config id={config['id']} "
          f"regime_platform_id={config['regime_platform_id']}")
    assert config["regime_platform_id"] == args.regime_platform_id

    # --- Symbolic forecast (regime-conditioned) ---
    forecast = api.predictions.symbolic_forecast(
        platform_id, prediction_config_id=config["id"],
    )

    print(f"Forecast value: {forecast['forecast']['value']}")
    print(f"Drivers fired: {len(forecast.get('why', []))}")

    # Regime provenance from the live single-classify
    prov = forecast.get("regime_provenance")
    if prov:
        print(f"Regime label: {prov['regime_label']}")
        print(f"Regime proof_checked: {prov['regime_proof_checked']}")
        print(f"Regime vocabulary: {prov.get('vocabulary')}")
    else:
        print("No regime provenance (regime platform may not be configured)")

    # Check for regime-conditioned rules in the WHY
    regime_rules = [
        d for d in forecast.get("why", [])
        if any("regime_" in f for f in (d.get("features") or []))
    ]
    print(f"Regime-conditioned rules: {len(regime_rules)}")

    print("Done.")


def main() -> None:
    run_demo(run, parse_args())


if __name__ == "__main__":
    main()
