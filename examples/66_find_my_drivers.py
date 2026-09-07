"""66 -- Find My Drivers -- discover the predictive drivers of a target.

Discovery mode is the MAINLINE Predictions usage: supply a target + candidate
features (no recipe), and the platform derives certified predictive drivers.
When a prediction config's ``feature_fields`` is null, the symbolic forecaster
auto-discovers ALL numeric columns as candidate drivers, induces human-readable
driver-rules, and ranks them by importance with holdout evidence.

The ``find_drivers`` convenience method wraps ``symbolic_forecast`` with
discovery-mode defaults. The response's ``driver_report`` is the headline: each
base series ranked by importance, with its holdout skill (the strongest single
driver's evidence), significance (fire rate), and provenance tag
(``discovered`` when feature_fields was null).

    python 66_find_my_drivers.py [platform_id]
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
    banner("Find My Drivers -- discovery-mode predictions")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform -- run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    # 1) Ensure a discovery-mode config exists (feature_fields=null).
    configs = api.predictions.list_configs(platform_id)
    config_id = None
    for c in configs:
        if c.get("discovery_mode"):
            config_id = c["id"]
            step(f"Found discovery-mode config #{config_id} (target={c['target_field']})")
            break
    if config_id is None:
        print("  No discovery-mode prediction config (feature_fields=null).")
        print("  Create one with: api.predictions.create_config(platform_id, target_field='...')")
        return

    # 2) Find the drivers.
    result = api.predictions.find_drivers(
        platform_id, prediction_config_id=config_id,
    )
    step(f"discovery_mode={result['discovery_mode']}")

    # 3) Read the ranked driver report.
    report = result["driver_report"]
    step(f"Discovered {len(report)} predictive driver(s):")
    for d in report:
        skill = d.get("holdout_skill")
        skill_str = f"{skill:.4f}" if skill is not None else "n/a"
        sig = d.get("significance")
        sig_str = f"{sig:.0%}" if sig is not None else "n/a"
        print(
            f"  {d['label']} ({d['series']}): "
            f"importance={d['importance_share']:.0%}, "
            f"strength={d['strength']}, "
            f"holdout_skill={skill_str}, "
            f"significance={sig_str}, "
            f"provenance={d.get('provenance', 'n/a')}"
        )

    # 4) The full forecast is still available.
    fc = result["forecast"]
    step(
        f"Forecast value={fc['value']} "
        f"[{fc['lower']}, {fc['upper']}] "
        f"(baseline={result['baseline']})"
    )

    # 5) The prediction_record is present for downstream consumption.
    record = result["prediction_record"]
    step(
        f"prediction_record: name={record['name']}, "
        f"value={record['value']}, "
        f"probability={record.get('probability')}"
    )


if __name__ == "__main__":
    main()
