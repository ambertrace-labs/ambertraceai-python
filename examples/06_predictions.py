"""06 — Predictions: configure, train, and run a forecast.

Demonstrates the prediction workflow on an existing platform: list configs,
create one, train it (async), then run a prediction. Pass a platform id as
argv[1], or it uses your first active platform.

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


def _wait_for_config(api, platform_id, config_id, *, timeout=300, poll_interval=5) -> str:
    """Poll a prediction config until training reaches a terminal status."""
    import time

    deadline = time.monotonic() + timeout
    while True:
        configs = api.predictions.list_configs(platform_id)
        cfg = next((c for c in configs if c.get("id") == config_id), None)
        status = (cfg or {}).get("status", "")
        if status in ("trained", "failed", "error"):
            return status
        if time.monotonic() >= deadline:
            return status or "unknown"
        time.sleep(poll_interval)


def main() -> None:
    api = get_client()
    banner("Predictions — configure / train / predict")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform — run 02_platform_lifecycle.py first, or pass a id.")
        return
    step(f"Using platform #{platform_id}")

    configs = api.predictions.list_configs(platform_id)
    step(f"{len(configs)} existing prediction config(s).")

    try:
        # target_field must be a column in the platform's dataset. cross_sectional
        # mode treats each row independently (no time index required).
        config = api.predictions.create_config(
            platform_id,
            mode="cross_sectional",
            target_field="risk_score",
        )
        config_id = config["id"]
        step(f"Created config #{config_id}")

        api.predictions.train(platform_id, config_id)
        # Training runs async. Its job id is not pollable via /jobs/{id}, so poll
        # the config's own `status` field (pending -> training -> trained/failed).
        status = _wait_for_config(api, platform_id, config_id, timeout=300)
        step(f"Training finished: status={status}")

        if status == "trained":
            result = api.predictions.predict(
                platform_id, input_data={"risk_score": 0.5}, config_id=config_id
            )
            step(f"Prediction: {result.get('prediction') or result}")
        else:
            step("Model not trained (the platform's data may not suit this target).")

        # Clean up the config we created.
        api.predictions.delete_config(platform_id, config_id)
        step(f"Deleted config #{config_id}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
        print("  (Prediction config shape may differ for this platform/domain.)")

    print("\n✓ Prediction walkthrough complete.")


if __name__ == "__main__":
    main()
