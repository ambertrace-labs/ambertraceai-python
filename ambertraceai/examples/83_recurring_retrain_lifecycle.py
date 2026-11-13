"""83 — Recurring forecaster: build once, retrain only on new data, audit every model.

The scheduled-job pattern for a forecaster, end to end on ONE domain, ONE platform and ONE
prediction config -- run it every night and it creates nothing it already has:

  1. ``domains.get_or_create`` -- the same name returns the SAME domain.
  2. Reuse the domain's dataset (``datasets.list``); upload only on the first run. Pass
     ``--dataset`` with fresh data to add a new dataset on a later run.
     (``upload`` / ``fetch`` / ``fetch_multi`` each CREATE a dataset; ``fetch`` writes.)
  3. Reuse the domain's active platform; build only when there is none.
  4. Reuse the platform's prediction config (``predictions.list_configs``); create only once.
  5. ``predictions.check_staleness`` -> ``train`` ONLY when the data changed (or never trained).
  6. ``predictions.model_history`` -- every model version with the datasets it was trained on.

Run it twice: the second run trains nothing. Add ``--dataset new.csv`` and it retrains in place.
(``symbolic_forecast(feature_overrides=)`` is a what-if on the frozen trained model -- not a retrain.)

    python 83_recurring_retrain_lifecycle.py [--dataset new.csv]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "environmental_monitoring.csv"

DOMAIN_NAME = "Recurring environmental forecast (reusable)"
DOMAIN_DESCRIPTION = (
    "Environmental pollution monitoring and compliance forecasting. "
    "Facilities are monitored for pollutant levels (nitrogen dioxide, "
    "particulate matter, sulphur dioxide, carbon monoxide, benzene, etc.) "
    "with readings taken over time. Each reading has a measurement value, "
    "a regulatory limit, and a permit limit. The goal is to forecast "
    "future measurement values based on historical trends, facility type, "
    "pollutant characteristics, and seasonal patterns."
)


def run_retrain_lifecycle(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Get or create the domain (idempotent)")
    domain = api.domains.get_or_create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']} created={domain['created']}")

    print_section(2, total, "Reuse the dataset; upload on first run or when --dataset is given")
    datasets = api.datasets.list(domain_id=domain["id"])
    if datasets and not args.dataset:
        dataset = datasets[0]
        print(f"  Reusing dataset {dataset['id']} ({len(datasets)} on this domain)")
    else:
        dataset = api.datasets.upload(
            domain_id=domain["id"], file_path=str(args.dataset or DEFAULT_DATASET))
        print(f"  Uploaded dataset {dataset['id']}")

    print_section(3, total, "Reuse the active platform, build only when there is none")
    platforms = api.platforms.list(domain_id=domain["id"], status="active")
    if platforms:
        platform = platforms[0]
        print(f"  Reusing platform {platform['id']}")
    else:
        if domain["created"] or domain.get("status") == "draft":
            build_ontology(api, domain["id"])
        platform = build_platform(api, domain["id"], dataset["id"])
        print(f"  Built platform {platform['id']}")

    print_section(4, total, "Reuse the prediction config, create only once")
    configs = api.predictions.list_configs(platform["id"])
    if configs:
        config = configs[0]
        print(f"  Reusing config {config['id']}")
    else:
        config = api.predictions.create_config(
            platform["id"], target_field="measurement_value",
            time_index_field="reading_date", horizon=1, frequency="monthly",
            model_type="auto")
        print(f"  Created config {config['id']}")

    print_section(5, total, "Retrain only if the data changed")
    try:
        status = api.predictions.check_staleness(platform["id"], config["id"])
        never_trained = status.get("model_version") is None
        data_changed = status["data_changed"]
        print(f"  data_changed={data_changed} model_version={status.get('model_version')}")
    except AmbertraceError as exc:
        if exc.status_code != 404:
            raise
        # A never-trained config has no active model to compare against: 404.
        never_trained, data_changed = True, False
        print("  No trained model yet for this config.")
    if never_trained or data_changed:
        train_prediction_model(api, platform["id"], config["id"])
        print("  Trained in place (same platform and config)")
    else:
        print("  Data unchanged -- skipping retrain.")

    print_section(6, total, "Audit: every model version and the data it used")
    for v in api.predictions.model_history(platform["id"], config["id"]):
        marker = "ACTIVE" if v.get("is_active") else "      "
        print(f"  {marker} model_version={v['model_version']} "
              f"trained_at={v.get('trained_at')} datasets={v.get('dataset_ids')}")
    print(f"\nDone. Domain {domain['id']} / platform {platform['id']} / config {config['id']} "
          "are reused on every run.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recurring forecaster -- build once, retrain only on new data, audit models",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=None,
                        help="Fresh CSV to upload on this run (default: upload "
                             "environmental_monitoring.csv only on the first run)")
    args = parser.parse_args()
    run_demo(run_retrain_lifecycle, args)


if __name__ == "__main__":
    main()
