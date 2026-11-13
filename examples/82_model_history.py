"""82 — Which model, trained on which data, was serving? (model_history)

A recurring forecaster retrains the SAME platform and config as data arrives. Each retrain
adds a model version and never overwrites an earlier one.
``predictions.model_history(platform_id, config_id)`` lists them all, newest first, each with
the datasets it was trained on, so a past forecast can be audited to its model and data. It
reads metadata only (no model is loaded).

  1. ``predictions.model_history`` -> every version with ``dataset_ids`` + fingerprint.
  2. Find the version serving now (``is_active``) and compare it with ``check_staleness``.

Needs a platform with a trained prediction config (see 16_timeseries_forecast.py).

    python 82_model_history.py --platform-id 12 --config-id 3
"""

from __future__ import annotations

import argparse

from _common import add_common_args, print_section, run_demo


def run_model_history(api, args: argparse.Namespace) -> None:
    total = 2

    print_section(1, total, "List every trained model version")
    versions = api.predictions.model_history(args.platform_id, args.config_id)
    if not versions:
        print("  No model trained yet for this config.")
        return
    for v in versions:
        marker = "ACTIVE" if v.get("is_active") else "      "
        print(f"  {marker} model_version={v['model_version']} trained_at={v.get('trained_at')} "
              f"datasets={v.get('dataset_ids')}")

    print_section(2, total, "Compare the serving version with the current data")
    active = next((v for v in versions if v.get("is_active")), versions[0])
    status = api.predictions.check_staleness(args.platform_id, args.config_id)
    same = status.get("model_version") == active["model_version"]
    print(f"  Serving model_version={active['model_version']} (staleness agrees: {same})")
    print(f"  Training data changed since then: {status['data_changed']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List a config's trained model versions")
    add_common_args(parser)
    parser.add_argument("--platform-id", type=int, required=True)
    parser.add_argument("--config-id", type=int, required=True,
                        help="A prediction config with one or more trained models")
    args = parser.parse_args()
    run_demo(run_model_history, args)


if __name__ == "__main__":
    main()
