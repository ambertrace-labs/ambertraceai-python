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
import sys

from _common import api, ensure_domain_platform_data

EXAMPLE_DATASET = "data/fred_economic_data.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Regime-conditioned forecast example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    parser.add_argument(
        "--regime-platform-id", type=int, required=True,
        help="ID of a built Decisions platform that classifies regimes")
    args = parser.parse_args()

    # --- Setup: domain + platform + data ---
    platform_id = ensure_domain_platform_data(
        domain_name="regime_forecast_demo",
        dataset_path=args.dataset,
    )

    # --- Create prediction config with regime conditioning ---
    config_resp = api.create_prediction_config(
        id=platform_id,
        data={
            "target_field": "GS10",
            "time_index_field": "date",
            "frequency": "monthly",
            "regime_platform_id": args.regime_platform_id,
        },
    )
    config = config_resp.data
    print(f"Created config id={config['id']} "
          f"regime_platform_id={config['regime_platform_id']}")
    assert config["regime_platform_id"] == args.regime_platform_id

    # --- Symbolic forecast (regime-conditioned) ---
    forecast_resp = api.symbolic_forecast(
        id=platform_id,
        data={"prediction_config_id": config["id"]},
    )
    forecast = forecast_resp.data

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


if __name__ == "__main__":
    sys.exit(main() or 0)
