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
from pathlib import Path

from _common import (
    add_common_args,
    run_demo,
    setup_forecast_platform,
)

EXAMPLE_DATASET = str(Path(__file__).resolve().parent / "data" / "fred_economic_data.csv")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combined neural+rule composition tier example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    add_common_args(parser)
    return parser.parse_args()


def run(api, args: argparse.Namespace) -> None:

    # --- Setup: domain + platform + data ---
    platform_id = setup_forecast_platform(
        api,
        name="combined_tier_demo",
        description="Combined neural+rule forecast of the US 10-year Treasury yield (GS10) from monthly FRED macro drivers.",
        dataset_path=args.dataset,
    )

    # --- Create config with neural baseline + sharpe objective ---
    config = api.predictions.create_config(
        platform_id,
        target_field="GS10",
        time_index_field="date",
        frequency="monthly",
        baseline_mode="neural",
        objective="sharpe_ratio",
    )
    print(f"Created config id={config['id']} "
          f"baseline_mode={config['baseline_mode']} "
          f"objective={config['objective']}")

    # --- Symbolic forecast ---
    forecast = api.predictions.symbolic_forecast(
        platform_id,
        prediction_config_id=config["id"],
        include_fitted_series=True,
    )

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
    comp = api.predictions.neurosymbolic_comparison(
        platform_id,
        prediction_config_id=config["id"],
        include_series=True,
    )
    delta = comp.get("delta") or {}
    print("\nNeurosymbolic comparison delta:")
    print(f"  r2:    {delta.get('r2')}")
    print(f"  rmse:  {delta.get('rmse')}")
    print(f"  objective: {delta.get('objective')}")
    obj_key = delta.get("objective", "skill_vs_persistence")
    if obj_key in delta and obj_key not in ("r2", "rmse"):
        print(f"  {obj_key}: {delta[obj_key]}")

    print("\nDone.")


def main() -> None:
    run_demo(run, parse_args())


if __name__ == "__main__":
    main()
