"""51 -- EIA general v2 catalog: browse + pull a non-oil energy dataset.

The ``eia`` connector supports two mutually-exclusive modes:

* **Mode A** -- preset oil series via ``series_ids`` (see example 24).
* **Mode B** -- the FULL EIA v2 catalog (electricity, natural gas, coal,
  nuclear, renewables, CO2 emissions, international, ...) via ``route`` +
  ``facets``.  Browse it first with ``api.connectors.eia_discover()``.

This example browses the catalog, then pulls monthly retail electricity
prices for California and Texas -- a non-oil dataset a preset can't reach.

Bring your own EIA key (free: https://www.eia.gov/opendata/register.php).
Add it to examples/.env as:
    EIA_API_KEY=your_eia_key

    python 51_eia_general_catalog.py
"""

import os
import sys

from _common import banner, get_client, step, wait_for_domain
from ambertraceai import AmbertraceError


def main() -> None:
    eia_key = os.environ.get("EIA_API_KEY")
    if not eia_key:
        sys.exit(
            "Set EIA_API_KEY in examples/.env "
            "(free at https://www.eia.gov/opendata/register.php)."
        )

    api = get_client()
    banner("EIA general v2 catalog (Mode B)")

    # --- 1. Browse the catalog --------------------------------------------
    top = api.connectors.eia_discover()
    routes = [r["id"] for r in top.get("routes", [])]
    step(f"Top-level EIA v2 routes ({len(routes)}): {routes}")

    leaf = api.connectors.eia_discover(route="electricity/retail-sales")
    facet_ids = [f["id"] for f in leaf.get("facets", [])]
    data_cols = list(leaf.get("data", {}).keys())
    step(f"electricity/retail-sales facets: {facet_ids}")
    step(f"electricity/retail-sales data columns: {data_cols}")

    # --- 2. Pull a non-oil dataset via Mode B -------------------------------
    domain = api.domains.create(
        name="SDK Example -- EIA General Catalog",
        description="Monthly retail electricity prices, CA vs TX (EIA v2).",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    platform_id = None
    try:
        dataset = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="eia",
            config={
                "api_key": eia_key,
                "route": "electricity/retail-sales",
                "facets": {"stateid": ["CA", "TX"], "sectorid": ["RES"]},
                "data": ["price", "sales"],
                "pivot_facet": "stateid",
                "frequency": "monthly",
            },
        )
        step(f"Ingested EIA general-catalog data: dataset #{dataset.get('id')}")

        api.domains.build_ontology(domain_id)
        if wait_for_domain(api, domain_id, timeout=240).get("status") != "active":
            step("Ontology build did not complete; aborting.")
            return

        result = api.platforms.create(domain_id=domain_id, dataset_id=dataset["id"])
        platform_id = result["platform"]["id"]
        api.wait_for_job(result["build_job"]["id"], timeout=600, type='build')
        step(f"Platform #{platform_id} built -- ready to query CA/TX retail "
             "electricity price and sales.")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
    finally:
        if platform_id:
            api.platforms.delete(platform_id)
        api.domains.delete(domain_id)
        step(f"Cleaned up platform + domain #{domain_id}")

    print("\n  EIA general-catalog walkthrough complete.")


if __name__ == "__main__":
    main()
