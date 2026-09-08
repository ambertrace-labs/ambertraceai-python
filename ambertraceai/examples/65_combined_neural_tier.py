"""65 -- Combined neural+rule composition tier.

Demonstrates the ``combined`` forecast tier: when
``baseline_mode='neural'`` and symbolic driver-rules fire, the forecast
composes onto the neural (GBT) prediction instead of persistence.

The response carries:
  - ``forecast_tier='combined'`` -- the neural+rules composition tier.
  - ``anchor_used='neural'`` -- confirms the GBT was used as the anchor.
  - ``baseline`` -- the neural anchor value (the GBT prediction).
  - ``forecast.value`` -- neural anchor + sum of fired rule effects.

When ``include_fitted_series=True``, each holdout point also carries:
  - ``neural`` -- the GBT anchor prediction at that point.
  - ``combined`` -- neural + sum of fired rule effects.

The neurosymbolic comparison (``/api/v1/.../neurosymbolic-comparison``)
now scores the correction-rule delta on the config's ``objective`` metric
(e.g. sharpe_ratio) when the objective is a trading metric. The ``delta``
dict includes the objective key alongside the standard r2/rmse deltas.

    python 65_combined_neural_tier.py

.. note::

   Requires a platform with ``baseline_mode='neural'`` (the default for new
   prediction configs) and at least one active driver-rule.
"""

import argparse
import sys

from _common import api, ensure_domain_platform_data

EXAMPLE_DATASET = "data/fred_economic_data.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Combined neural+rule composition tier example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    args = parser.parse_args()

    # --- Setup: domain + platform + data ---
    platform_id = ensure_domain_platform_data(
        domain_name="combined_tier_demo",
        dataset_path=args.dataset,
    )

    # --- Create config with neural baseline + sharpe objective ---
    config_resp = api.create_prediction_config(
        id=platform_id,
        data={
            "target_field": "GS10",
            "time_index_field": "date",
            "frequency": "monthly",
            "baseline_mode": "neural",
            "objective": "sharpe_ratio",
        },
    )
    config = config_resp.data
    print(f"Created config id={config['id']} "
          f"baseline_mode={config['baseline_mode']} "
          f"objective={config['objective']}")

    # --- Symbolic forecast ---
    forecast_resp = api.symbolic_forecast(
        id=platform_id,
        data={
            "config_id": config["id"],
            "include_fitted_series": True,
        },
    )
    forecast = forecast_resp.data

    # --- Combined tier ---
    tier = forecast.get("forecast_tier")
    anchor_used = forecast.get("anchor_used")
    drivers_fired = forecast.get("drivers_fired", 0)
    print(f"\nForecast tier:  {tier}")
    print(f"Anchor used:    {anchor_used}")
    print(f"Drivers fired:  {drivers_fired}")
    print(f"Baseline:       {forecast.get('baseline')}")
    print(f"Value:          {forecast.get('forecast', {}).get('value')}")

    if tier == "combined" and anchor_used == "neural":
        print("  -> Forecast composed onto the neural (GBT) prediction.")

    # --- Per-point neural/combined columns ---
    fs = forecast.get("fitted_series") or {}
    series = fs.get("series") or []
    if series:
        print(f"\nFitted series ({len(series)} holdout points):")
        for pt in series[:5]:
            print(f"  index={pt['index']}  actual={pt.get('actual'):.4f}  "
                  f"neural={pt.get('neural')}  combined={pt.get('combined')}  "
                  f"fired_rules={pt.get('fired_rules')}")
        if len(series) > 5:
            print(f"  ... {len(series) - 5} more points")

    # --- Neurosymbolic comparison with objective-scored delta ---
    comparison_resp = api.neurosymbolic_comparison(
        id=platform_id,
        data={
            "config_id": config["id"],
            "include_series": True,
        },
    )
    comp = comparison_resp.data
    delta = comp.get("delta") or {}
    print("\nNeurosymbolic comparison delta:")
    print(f"  r2:    {delta.get('r2')}")
    print(f"  rmse:  {delta.get('rmse')}")
    print(f"  objective: {delta.get('objective')}")
    obj_key = delta.get("objective", "skill_vs_persistence")
    if obj_key in delta and obj_key not in ("r2", "rmse"):
        print(f"  {obj_key}: {delta[obj_key]}")

    print("\nDone.")


if __name__ == "__main__":
    sys.exit(main() or 0)
