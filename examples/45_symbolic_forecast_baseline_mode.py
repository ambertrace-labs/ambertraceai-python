"""45 -- Symbolic forecast with selectable baseline_mode anchor.

Demonstrates the ``baseline_mode`` config parameter that controls the forecast
anchor the symbolic forecaster composes driver effects onto:

- **persistence** (default) -- last observed level. Today's behaviour.
- **climatology** -- fit-window mean. The forecast anchors on the historical
  average; useful when the latest level is an outlier or you want a
  mean-reversion framing. Caveat: on a strongly trending series the anchor can
  sit far from the latest level -- check ``skill_vs_persistence`` to confirm the
  drivers still beat the persistence yardstick.
- **drift** -- last level + h * OLS slope. A linear-trend anchor.

The holdout A/B acceptance gate recomposes driver effects onto the chosen anchor
so accepted drivers are not mis-scaled. ``skill_vs_persistence`` is ALWAYS
reported as the external yardstick regardless of which anchor is active.

    python 45_symbolic_forecast_baseline_mode.py [platform_id]
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
    banner("Symbolic forecast -- selectable baseline_mode anchor")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform -- run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    # Create a prediction config with baseline_mode='climatology'.
    # The symbolic forecaster will anchor on the fit-window mean instead of
    # the last observed level, and recompose the holdout A/B acceptance
    # base accordingly.
    config_id = None
    try:
        config = api.predictions.create_config(
            platform_id,
            mode="timeseries",
            target_field="value",
            time_index_field="date",
            horizon=1,
            frequency="monthly",
            baseline_mode="climatology",
        )
        config_id = config["id"]
        step(
            f"Created config #{config_id} "
            f"(baseline_mode={config.get('baseline_mode')})"
        )

        # Run a symbolic forecast. The baseline in the response is the
        # climatology anchor (fit-window mean), NOT the last observed level.
        result = api.predictions.symbolic_forecast(
            platform_id, prediction_config_id=config_id,
        )
        fc = result["forecast"]
        step(
            f"Forecast value={fc['value']} "
            f"[{fc['lower']}, {fc['upper']}]"
        )
        step(f"Baseline (climatology anchor) = {result['baseline']}")
        step(f"Anchor mode = {result.get('baseline_mode')}")

        # skill_vs_persistence is always reported as the external yardstick,
        # even though the model's own anchor is climatology.
        step(f"skill_vs_persistence = {result.get('skill_vs_persistence')}")

    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
        print("  (The symbolic forecast feature flag may be disabled, or the")
        print("  platform's data may not have a 'value'/'date' column.)")
    finally:
        if config_id is not None:
            api.predictions.delete_config(platform_id, config_id)
            step(f"Deleted config #{config_id}")

    print("\nDone.")


if __name__ == "__main__":
    main()
