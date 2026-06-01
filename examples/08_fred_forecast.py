"""08 — FRED forecast: ingest real macro data and forecast a series.

A finance-grade end-to-end run on live data:
    FRED connector (yields, fed funds, CPI) → domain → platform →
    explainable time-series forecast of the 10-year Treasury yield.

Bring your own FRED key (free: https://fred.stlouisfed.org → My Account → API
Keys). Add it to examples/.env as:
    FRED_API_KEY=your_fred_key

    python 08_fred_forecast.py
"""

import os
import sys

from _common import banner, get_client, step, wait_for_domain
from ambertraceai import AmbertraceError

SERIES = ["GS10", "FEDFUNDS", "CPIAUCSL"]  # 10y yield, fed funds rate, CPI
TARGET = "GS10"


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
    fred_key = os.environ.get("FRED_API_KEY")
    if not fred_key:
        sys.exit("Set FRED_API_KEY in examples/.env (free at https://fred.stlouisfed.org).")

    api = get_client()
    banner("FRED macro forecast")

    domain = api.domains.create(
        name="SDK Example — Macro Rates",
        description="US interest rates and inflation: 10y Treasury yield, fed funds, CPI.",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    platform_id = None
    try:
        dataset = api.datasets.fetch(
            domain_id=domain_id, connector_type="fred",
            config={"api_key": fred_key, "series_ids": SERIES, "frequency": "monthly"},
        )
        step(f"Ingested FRED data: dataset #{dataset.get('id')} ({SERIES})")

        api.domains.build_ontology(domain_id)
        if wait_for_domain(api, domain_id, timeout=240).get("status") != "active":
            step("Ontology build did not complete; aborting.")
            return

        result = api.platforms.create(domain_id=domain_id, dataset_id=dataset["id"])
        platform_id = result["platform"]["id"]
        api.wait_for_job(result["build_job"]["id"], timeout=600)
        step(f"Platform #{platform_id} built")

        config = api.predictions.create_config(
            platform_id, mode="timeseries", target_field=TARGET,
            time_index_field="date", horizon=3, frequency="monthly",
        )
        api.predictions.train(platform_id, config["id"])
        status = _config_status(api, platform_id, config["id"])
        step(f"Training: {status}")

        if status == "trained":
            forecast = api.predictions.predict(platform_id, prediction_config_id=config["id"])
            step(f"3-month {TARGET} forecast: {forecast.get('prediction') or forecast}")
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

    print("\n✓ FRED forecast walkthrough complete.")


if __name__ == "__main__":
    main()
