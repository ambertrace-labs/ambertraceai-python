"""72 -- Cross-sectional regression: categorical features + a regression objective.

A ``cross_sectional`` prediction config treats every row as an independent
example (no time axis). This walkthrough uses a bundled model-cost panel
(numeric ``log_flop`` / ``log_params`` / ``log_dataset_size``, categorical
``domain`` / ``open_weights``, regression target ``log_cost``):

  1. Create a domain + upload the panel, build the platform.
  2. ``predictions.create_config(mode="cross_sectional", objective="rmse")`` --
     the regression objectives are ``"rmse"`` (the cross_sectional default),
     ``"mae"`` and ``"r_squared"``; they drive ``model_type="auto"`` selection
     and the admission of correction rules. Trading objectives and
     ``skill_vs_persistence`` are time-series only.
  3. Train, then ``predict``. String-categorical columns are one-hot encoded as
     at training: pass them in ``feature_overrides`` (``{"domain": "Language"}``;
     an unseen level is listed in ``unmatched_overrides``). Features you OMIT are
     imputed with the TRAINING mean, so a sparse row (just ``log_flop``) still
     predicts near the data's centre rather than collapsing.
  4. ``symbolic_forecast`` on a cross_sectional config reports a K-fold holdout
     (``fitted_series.basis == "k_fold_cross_validation"``): no lag / rolling
     drivers, no persistence baseline, ``skill_vs_persistence`` is null.

Creates resources on your account. Run with --help for options.

    python 72_cross_sectional_regression.py
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    create_domain,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "model_cost_panel.csv"

DOMAIN_NAME = "Model cost panel (cross-sectional regression)"
DOMAIN_DESCRIPTION = (
    "Training-cost estimates for machine-learning models. Each row is one model: "
    "its compute (log_flop), size (log_params), data (log_dataset_size), "
    "application domain and whether the weights are open. The target is log_cost."
)


def run_regression(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Domain, data and platform")
    domain = create_domain(api, name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    domain = build_ontology(api, domain["id"])
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']} ready")

    print_section(2, total, "Cross-sectional config with a regression objective")
    config = api.predictions.create_config(
        platform["id"], mode="cross_sectional", target_field="log_cost",
        model_type="auto", objective="rmse",
    )
    print(f"  Config {config['id']}: objective={config['objective']} "
          f"eval_metric={config.get('eval_metric')}")
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Trained: status={config.get('status')}")

    print_section(3, total, "Predict: categorical override + a sparse row")
    for label, row in (
        ("Language, open", {"log_flop": 24.0, "log_params": 10.0,
                            "log_dataset_size": 12.0, "domain": "Language",
                            "open_weights": True}),
        ("Games, open", {"log_flop": 24.0, "log_params": 10.0,
                         "log_dataset_size": 12.0, "domain": "Games",
                         "open_weights": True}),
        ("sparse (log_flop only)", {"log_flop": 25.0}),
    ):
        result = api.predictions.predict(
            platform["id"], prediction_config_id=config["id"],
            feature_overrides=row)
        pred = result.get("prediction") or result
        print(f"  {label}: log_cost={pred.get('value')} "
              f"unmatched_overrides={result.get('unmatched_overrides')}")

    print_section(4, total, "Symbolic forecast: K-fold holdout")
    forecast = api.predictions.symbolic_forecast(
        platform["id"], prediction_config_id=config["id"],
        include_fitted_series=True)
    series = forecast.get("fitted_series") or {}
    print(f"  basis={series.get('basis')} "
          f"skill_vs_persistence={forecast.get('skill_vs_persistence')} "
          f"objective={forecast.get('objective')}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Cross-sectional regression with categorical features")
    add_common_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="Path to the panel CSV (default: %(default)s)")
    args = parser.parse_args()
    run_demo(run_regression, args)


if __name__ == "__main__":
    main()
