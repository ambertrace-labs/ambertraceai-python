"""81 — Retrain only when the data changed (check_staleness).

A recurring forecaster should keep ONE platform and retrain it on fresh data -- and only
when the data actually changed. ``predictions.check_staleness(platform_id, config_id)``
compares a content fingerprint of the datasets a retrain would use now with the one the
active model was trained on. It reads dataset files only (no model is loaded).

  1. Optionally upload fresh data to the platform's domain (``--dataset``).
  2. ``predictions.check_staleness`` -> ``data_changed`` + both fingerprints.
  3. If ``data_changed``: ``predictions.train`` retrains in place (same platform and
     config); a second check then reports ``data_changed`` False.

Needs a platform with a trained prediction config (see 16_timeseries_forecast.py).

    python 81_retrain_when_data_changed.py --platform-id 12 --config-id 3 [--dataset new.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import add_common_args, print_section, run_demo, train_prediction_model


def run_staleness(api, args: argparse.Namespace) -> None:
    total = 3

    print_section(1, total, "Upload fresh data (optional)")
    if args.dataset:
        domain_id = api.platforms.get(args.platform_id)["domain_id"]
        dataset = api.datasets.upload(domain_id=domain_id, file_path=str(args.dataset))
        print(f"  Uploaded dataset {dataset['id']} to domain {domain_id}")
    else:
        print("  No --dataset given; checking the data as it stands")

    print_section(2, total, "Has the training data changed?")
    status = api.predictions.check_staleness(args.platform_id, args.config_id)
    print(f"  data_changed={status['data_changed']}  model_version={status.get('model_version')}")
    print(f"  trained on {status.get('training_data_fingerprint')}")
    print(f"  now        {status.get('current_data_fingerprint')} "
          f"(datasets {status.get('current_dataset_ids')})")

    print_section(3, total, "Retrain only if it changed")
    if not status["data_changed"]:
        print("  Data unchanged -- skipping retrain.")
        return
    train_prediction_model(api, args.platform_id, args.config_id)
    after = api.predictions.check_staleness(args.platform_id, args.config_id)
    print(f"  Retrained in place: model_version={after.get('model_version')} "
          f"data_changed={after['data_changed']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Retrain only when the data changed")
    add_common_args(parser)
    parser.add_argument("--platform-id", type=int, required=True)
    parser.add_argument("--config-id", type=int, required=True,
                        help="A prediction config that already has a trained model")
    parser.add_argument("--dataset", type=Path, default=None,
                        help="Fresh CSV to upload to the platform's domain before checking")
    args = parser.parse_args()
    run_demo(run_staleness, args)


if __name__ == "__main__":
    main()
