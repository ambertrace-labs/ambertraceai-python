"""63 -- Sharpe-ratio objective forecast.

Demonstrates the ``objective`` field on PredictionConfig: creating a
prediction config with ``objective='sharpe_ratio'`` so the acceptance gate
optimises for RISK-ADJUSTED directional PnL instead of the default
skill-vs-persistence metric.

The per-objective trading metrics (directional_pnl, hit_rate, sharpe_ratio,
max_drawdown) are surfaced in the symbolic-forecast response metadata when the
config declares a ``frequency``.

When ``include_fitted_series=True``, the ``per_tier_skill`` block carries
per-tier trading metrics: ``per_tier_skill['composed']`` contains
trading metrics on the composed prediction, ``per_tier_skill['rule_layer']``
shows the symbolic rules' standalone trading performance, and
``per_tier_skill['neural']`` shows the GBT baseline's standalone trading
performance.  The headline ``objective_value`` describes the tier
the served forecast comes from (the ``served_tier`` key names it); under the
default neural anchor that is ``composed``.

    python 63_sharpe_objective_forecast.py

.. note::

   Under the default ``baseline_mode='neural'`` the served forecast is the
   composed path (neural anchor plus fired rule effects), so ``served_tier``
   is ``composed`` and the headline matches ``per_tier_skill['composed']``;
   ``per_tier_skill`` still lists every tier's metrics, including any tier
   that scores higher on the configured ``objective``.
   ``baseline_mode='persistence'`` is not supported -- a forecast
   derived from the last observed value moves with spot and is untradeable.
   Persistence remains as a reference metric (``skill_vs_persistence``).
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
        description="Sharpe-ratio objective forecast example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    add_common_args(parser)
    return parser.parse_args()


def run(api, args: argparse.Namespace) -> None:

    # --- Setup: domain + platform + data ---
    platform_id = setup_forecast_platform(
        api,
        name="sharpe_objective_demo",
        description="Sharpe-ratio objective forecast of the US 10-year Treasury yield (GS10) from monthly FRED macro drivers.",
        dataset_path=args.dataset,
    )

    # --- Create prediction config with objective='sharpe_ratio' ---
    config = api.predictions.create_config(
        platform_id,
        target_field="GS10",
        time_index_field="date",
        frequency="monthly",
        objective="sharpe_ratio",
    )
    print(f"Created config id={config['id']} objective={config['objective']}")
    assert config["objective"] == "sharpe_ratio"

    # --- Train ---
    trained = api.predictions.train(platform_id, config["id"])
    print(f"Training status: {trained.get('status', 'unknown')}")

    # --- Symbolic forecast (surfaces the per-objective metrics) ---
    forecast = api.predictions.symbolic_forecast(
        platform_id, prediction_config_id=config["id"],
    )

    # The response surfaces backtest-fit skill + objective-specific metrics
    print(f"Skill vs persistence: {forecast.get('skill_vs_persistence')}")
    print(f"Objective: {forecast.get('objective')}")
    print(f"Objective value: {forecast.get('objective_value')}")

    # Trading metrics are in the response when frequency is set
    for key in ("directional_pnl", "hit_rate", "sharpe_ratio", "max_drawdown"):
        val = forecast.get(key)
        if val is not None:
            print(f"  {key}: {val}")

    # --- Per-tier trading metrics ---
    # Request the fitted series to get per_tier_skill with trading metrics.
    fs_data = api.predictions.symbolic_forecast(
        platform_id,
        prediction_config_id=config["id"],
        include_fitted_series=True,
    )
    per_tier_skill = fs_data.get("per_tier_skill") or {}

    # The composed entry carries trading metrics for the full composed
    # prediction.  The headline objective_value describes the tier the served
    # forecast comes from (named in served_tier; composed under neural mode).
    print(f"\nServed tier: {fs_data.get('served_tier', 'N/A')}")
    composed = per_tier_skill.get("composed")
    if composed:
        print("\nPer-tier trading metrics (composed):")
        for key in ("directional_pnl", "sharpe_ratio", "hit_rate",
                     "max_drawdown"):
            print(f"  composed.{key}: {composed.get(key)}")

    # The rule_layer entry shows the symbolic rules' standalone trading perf.
    rule_layer = per_tier_skill.get("rule_layer")
    if rule_layer:
        print("\nPer-tier trading metrics (rule_layer):")
        for key in ("directional_pnl", "sharpe_ratio", "hit_rate",
                     "max_drawdown"):
            print(f"  rule_layer.{key}: {rule_layer.get(key)}")

    # The neural entry shows the GBT baseline's standalone trading perf.
    neural = per_tier_skill.get("neural")
    if neural:
        print("\nPer-tier trading metrics (neural = GBT baseline):")
        for key in ("directional_pnl", "sharpe_ratio", "hit_rate",
                     "max_drawdown"):
            print(f"  neural.{key}: {neural.get(key)}")

    print("Done.")


def main() -> None:
    run_demo(run, parse_args())


if __name__ == "__main__":
    main()
