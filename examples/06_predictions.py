"""06 — Predictions: configure, train, and run a forecast.

Demonstrates the prediction workflow on an existing platform: list configs,
create a cross-sectional config, train it, then run a prediction. Pass a
platform id as argv[1], or it uses your first active platform.

    python 06_predictions.py [platform_id]
"""

import sys

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def _pick_platform(api, argv) -> int | None:
    if len(argv) > 1:
        return int(argv[1])
    for p in api.platforms.list():
        if p.get("status") in ("active", "ready"):
            return p["id"]
    return None


def main() -> None:
    api = get_client()
    banner("Predictions — configure / train / predict")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform — run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    configs = api.predictions.list_configs(platform_id)
    step(f"{len(configs)} existing prediction config(s).")

    config_id = None
    try:
        # target_field must be a column in the platform's dataset. cross_sectional
        # mode treats each ROW as an independent example (no time index / horizon):
        # on predict() the feature_overrides ARE the input row.
        config = api.predictions.create_config(
            platform_id,
            mode="cross_sectional",
            target_field="risk_score",
        )
        config_id = config["id"]
        step(f"Created config #{config_id} (mode={config.get('mode')})")

        # Since 1.0.0 train() blocks by default (wait=True): it polls the training
        # job to completion and returns the SETTLED trained config — no manual
        # poll-then-refetch. (Pass wait=False for the raw job envelope instead.)
        # A failed training job raises AmbertraceError.
        config = api.predictions.train(platform_id, config_id)
        status = config.get("status", "unknown")
        step(f"Training finished: status={status}")

        if status == "trained":
            # cross_sectional: feature_overrides is the input row to score.
            result = api.predictions.predict(
                platform_id,
                prediction_config_id=config_id,
                feature_overrides={"risk_score": 0.5},
            )
            step(f"Prediction: {result.get('prediction') or result}")
        else:
            step("Model not trained (the platform's data may not suit this target).")

    except AmbertraceError as e:
        # Narrow: only API errors land here (an SDK-misuse TypeError would surface
        # loudly rather than be mislabelled as a data-shape problem). The predict
        # config shape can legitimately differ per platform/domain.
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
        print("  (This platform/domain may not have a 'risk_score' column to predict.)")
    finally:
        # Clean up the config we created, if any.
        if config_id is not None:
            api.predictions.delete_config(platform_id, config_id)
            step(f"Deleted config #{config_id}")

    print("\n✓ Prediction walkthrough complete.")


if __name__ == "__main__":
    main()
