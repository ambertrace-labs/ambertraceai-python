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
trading metrics on the composed prediction (identical to the headline metrics),
``per_tier_skill['rule_layer']`` shows the symbolic rules' standalone
trading performance, and ``per_tier_skill['neural']`` shows the GBT
baseline's standalone trading performance.

    python 63_sharpe_objective_forecast.py

.. note::

   The ``objective`` field is available in the current SDK release.
   The configured objective currently does not drive rule acceptance.
"""

import argparse
import sys

from _common import api, ensure_domain_platform_data

EXAMPLE_DATASET = "data/fred_economic_data.csv"


def main():
    parser = argparse.ArgumentParser(
        description="Sharpe-ratio objective forecast example")
    parser.add_argument(
        "--dataset", default=EXAMPLE_DATASET,
        help="Path to the dataset CSV (default: %(default)s)")
    args = parser.parse_args()

    # --- Setup: domain + platform + data ---
    platform_id = ensure_domain_platform_data(
        domain_name="sharpe_objective_demo",
        dataset_path=args.dataset,
    )

    # --- Create prediction config with objective='sharpe_ratio' ---
    config_resp = api.create_prediction_config(
        id=platform_id,
        data={
            "target_field": "GS10",
            "time_index_field": "date",
            "frequency": "monthly",
            "objective": "sharpe_ratio",
        },
    )
    config = config_resp.data
    print(f"Created config id={config['id']} objective={config['objective']}")
    assert config["objective"] == "sharpe_ratio"

    # --- Train ---
    train_resp = api.train_prediction_model(
        id=platform_id,
        config_id=config["id"],
    )
    print(f"Training status: {train_resp.data.get('status', 'unknown')}")

    # --- Symbolic forecast (surfaces the per-objective metrics) ---
    forecast_resp = api.symbolic_forecast(
        id=platform_id,
        data={"config_id": config["id"]},
    )
    forecast = forecast_resp.data

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
    fs_resp = api.symbolic_forecast(
        id=platform_id,
        data={
            "config_id": config["id"],
            "include_fitted_series": True,
        },
    )
    fs_data = fs_resp.data
    per_tier_skill = fs_data.get("per_tier_skill") or {}

    # The composed entry carries the SAME trading metrics as the headline.
    composed = per_tier_skill.get("composed")
    if composed:
        print("\nPer-tier trading metrics (composed = headline):")
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


if __name__ == "__main__":
    sys.exit(main() or 0)
