"""46 -- Tiered coverage forecast with neural confidence gate.

Demonstrates the ``neural_confidence_tau`` config parameter that activates
the per-point GBT neural-tier confidence gate:

- **tau=0.0** (default) -- the gate labels every prediction with its
  ``forecast_tier`` and ``confidence`` but does NOT replace below-tau
  predictions. Backward-compatible: the ``value`` is always the GBT output.
- **tau>0** (e.g. 0.5) -- the gate REPLACES below-tau GBT predictions with
  the **climatology floor** (the fit-window target LEVEL mean -- a genuine
  non-persistence anchor). The ``forecast_tier`` is ``neural_scored@<tau>``
  when admitted, ``climatology_floor`` when floored.

The two-axis gate (Axis A: in-training-range OOD gate; Axis B: interval
sharpness) mirrors the ``ScoredDetermination`` trust-tier pattern
(example 41) but for regressors, not classifiers.

    python 46_tiered_coverage_forecast.py [platform_id]
"""

import sys

from _common import banner, get_client, step


def _pick_platform(api, argv) -> int | None:
    if len(argv) > 1:
        return int(argv[1])
    for p in api.platforms.list():
        if p.get("status") in ("active", "ready"):
            return p["id"]
    return None


def main() -> None:
    api = get_client()
    banner("Tiered coverage forecast -- neural confidence gate")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform -- run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    # Find or create a prediction config with the confidence gate active.
    # neural_confidence_tau=0.5 means: GBT predictions with two-axis
    # confidence >= 0.5 are admitted as 'neural_scored@0.5'; below 0.5
    # the point falls to the climatology floor (fit-window level mean).
    configs = api.platforms.list_prediction_configs(platform_id)
    config_id = None
    for c in configs:
        if c.get("neural_confidence_tau", 0.0) > 0:
            config_id = c["id"]
            break

    if config_id is None:
        step("Creating a prediction config with neural_confidence_tau=0.5")
        try:
            config = api.platforms.create_prediction_config(
                platform_id,
                target_field="value",
                time_index_field="date",
                horizon=1,
                frequency="monthly",
                neural_confidence_tau=0.5,
            )
            config_id = config["id"]
            step(f"  Created config #{config_id}")
        except Exception as e:
            print(f"  Could not create config: {e}")
            return

    # Run a prediction -- the response now carries tiering fields.
    step(f"Running prediction with config #{config_id}")
    try:
        result = api.platforms.predict(
            platform_id, prediction_config_id=config_id, explain=False,
        )
    except Exception as e:
        print(f"  Prediction failed: {e}")
        return

    pred = result.get("prediction", {})
    step("Prediction result:")
    print(f"  value           : {pred.get('value')}")
    print(f"  forecast_tier   : {pred.get('forecast_tier')}")
    print(f"  confidence      : {pred.get('confidence')}")
    print(f"  value_space     : {pred.get('value_space')}")

    basis = pred.get("confidence_basis")
    if basis:
        step("Confidence basis (two-axis gate):")
        print(f"  method          : {basis.get('method')}")
        print(f"  in_range        : {basis.get('in_range')}")
        print(f"  tau             : {basis.get('tau')}")
        print(f"  certified       : {basis.get('certified')}")
        if basis.get("uncertified_reason"):
            print(f"  reason          : {basis.get('uncertified_reason')}")

    step("Done.")


if __name__ == "__main__":
    main()
