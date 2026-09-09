"""52 -- Swap-curve slope: fetch_multi -> derive_column -> forecast.

The motivating case: a customer needs a forecast target that is an ARITHMETIC
COMBINATION of two connector-sourced columns (e.g. the EUR 10Y-2Y swap-curve
slope), with independent driver discovery ON the slope itself -- not on each
leg separately. Previously this was unbuildable: there was no way to derive
a new dataset column from two existing columns server-side, and no way to
pull a connector's raw row-level data back to the caller's process either.

Flow:
    1. fetch_multi() the two swap-curve legs (EUR 10Y, EUR 2Y) as ONE
       date-aligned panel (namespaced by connector type:
       ``swap_curves__EUR_10Y`` / ``swap_curves__EUR_2Y``).
    2. datasets.derive_column() the slope = 10Y - 2Y. drop_source_columns=True
       (the default) removes the two legs from the panel -- otherwise they
       would be auto-picked-up as driver candidates and, being a LINEAR
       function of the slope, would mechanically (and uselessly) "explain"
       it perfectly.
    3. predictions.create_config(target_field=<the derived slope column>) --
       the derived column resolves exactly like any other panel column, no
       different API surface.
    4. Train + forecast -- driver discovery runs on the SLOPE, not the legs.

No API key required (DTCC PPD is public, no-auth); network access to
kgc0418-tdw-data-0.s3.amazonaws.com is required for the live connector fetch.

    python 52_swap_curve_slope_forecast.py
"""

from _common import banner, get_client, step, wait_for_dataset, wait_for_domain
from ambertraceai import AmbertraceError

LEG_10Y = "swap_curves__EUR_10Y"
LEG_2Y = "swap_curves__EUR_2Y"
SLOPE_COLUMN = "eur_10y_2y_slope"


def _config_status(api, platform_id, config_id, *, timeout=300, poll_interval=5) -> str:
    import time
    deadline = time.monotonic() + timeout
    while True:
        cfg = next((c for c in api.predictions.list_configs(platform_id)
                    if c.get("id") == config_id), None)
        status = (cfg or {}).get("status", "")
        if status in ("trained", "failed", "error") or time.monotonic() >= deadline:
            return status
        time.sleep(poll_interval)


def main() -> None:
    api = get_client()
    banner("EUR swap-curve slope forecast (10Y - 2Y)")

    domain = api.domains.create(
        name="SDK Example — EUR Swap Curve Slope",
        description="EUR OIS swap curve 10Y/2Y slope, forecast with driver discovery.",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    platform_id = None
    try:
        # 1. fetch_multi the two legs as ONE date-aligned panel.
        dataset = api.datasets.fetch_multi(
            domain_id=domain_id,
            sources=[
                {"connector_type": "swap_curves",
                 "config": {"currencies": ["EUR"], "tenors": ["10Y"], "max_backfill_days": 30}},
                {"connector_type": "swap_curves",
                 "config": {"currencies": ["EUR"], "tenors": ["2Y"], "max_backfill_days": 30}},
            ],
            frequency="monthly", aggregation="last",
        )
        dataset = wait_for_dataset(api, dataset["id"])
        step(f"Fetched panel: dataset #{dataset['id']} "
             f"({dataset.get('row_count')} rows, {dataset.get('column_count')} cols)")

        # 2. Derive the slope; drop_source_columns=True (default) removes the
        # two legs so they can never be auto-selected as trivial drivers of
        # their own derivation.
        dataset = api.datasets.derive_column(
            dataset["id"], new_column=SLOPE_COLUMN,
            left=LEG_10Y, op="subtract", right=LEG_2Y,
        )
        remaining_columns = {
            c.get("name") for c in (dataset.get("schema_info") or {}).get("columns", [])
        }
        step(f"Derived '{SLOPE_COLUMN}' = {LEG_10Y} - {LEG_2Y}; "
             f"dataset now has {dataset.get('column_count')} columns "
             f"(legs dropped: {LEG_10Y not in remaining_columns})")

        api.domains.build_ontology(domain_id)
        if wait_for_domain(api, domain_id, timeout=240).get("status") != "active":
            step("Ontology build did not complete; aborting.")
            return

        result = api.platforms.create(domain_id=domain_id, dataset_id=dataset["id"])
        platform_id = result["platform"]["id"]
        api.wait_for_job(result["build_job"]["id"], timeout=600, type='build')
        step(f"Platform #{platform_id} built")

        # 3. The derived column IS the target -- resolved at train time like
        # any other panel column, no different API.
        config = api.predictions.create_config(
            platform_id, mode="timeseries", target_field=SLOPE_COLUMN,
            time_index_field="date", horizon=1, frequency="monthly",
        )
        api.predictions.train(platform_id, config["id"])
        status = _config_status(api, platform_id, config["id"])
        step(f"Training: {status}")

        if status == "trained":
            forecast = api.predictions.predict(
                platform_id, prediction_config_id=config["id"], explain=True,
            )
            step(f"1-month {SLOPE_COLUMN} forecast: "
                 f"{forecast.get('prediction') or forecast}")
            # 4. Driver discovery ran ON THE SLOPE -- inspect which panel
            # columns (never the dropped legs) explain its movement.
            explanation = forecast.get("explanation") or {}
            drivers = [f.get("feature") for f in explanation.get("feature_importance") or []]
            step(f"Top drivers of the slope: {drivers[:5]}")
        api.predictions.delete_config(platform_id, config["id"])
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
    finally:
        # Delete the platform first (its children aren't covered by the domain
        # delete cascade), then the domain.
        if platform_id:
            api.platforms.delete(platform_id)
        api.domains.delete(domain_id)
        step(f"Cleaned up platform + domain #{domain_id}")

    print("\n✓ Swap-curve slope forecast walkthrough complete.")


if __name__ == "__main__":
    main()
