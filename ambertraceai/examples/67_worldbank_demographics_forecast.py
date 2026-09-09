"""67 -- World Bank demographics and macro indicators as forecast covariates.

Demonstrates the ``worldbank`` connector: fetch GDP, CPI inflation, and
population growth for multiple countries from the World Bank Indicators API
(no API key required), then show how the resulting dataset is consumed as
covariates by the Predictions pipeline.

The World Bank connector delivers:

  * **Multi-indicator, multi-country panels** -- each config names a list
    of indicator codes and ISO-3166 alpha-3 country codes. The connector
    pivots the API's long-format records into a wide DataFrame with one
    column per (indicator, country) pair, named ``{indicator}_{country}``
    (e.g. ``NY.GDP.MKTP.CD_GBR``).
  * **No API key** -- the World Bank Indicators API v2 is free and
    keyless.  Data is licensed under CC BY 4.0 (attribution required;
    commercial use and redistribution permitted).
  * **Date-range filtering** -- ``start_date`` and ``end_date`` restrict
    the year range fetched (the API operates at annual granularity).
  * **Country-code normalisation** -- lowercase codes (e.g. ``gbr``) are
    normalised to uppercase (``GBR``) in both the API request and the
    resulting column names.

Covariates path: once the dataset is fetched into a domain, the
Predictions pipeline discovers all usable datasets in that domain
automatically (``resolve_usable_datasets``).  Configure a
``PredictionConfig`` with a ``target_field`` pointing at one column
(e.g. ``NY.GDP.MKTP.CD_GBR``), and the remaining columns become
covariates for the forecast.  No additional plumbing is needed --
the dataset simply needs to be in the same domain as the prediction
config.

Prerequisites:
    * ``AMBERTRACE_API_KEY`` -- your Ambertrace API key (see examples/.env).
    * No additional API key required -- the World Bank API is public.

    python 67_worldbank_demographics_forecast.py [--domain-id N]
"""

from __future__ import annotations

import sys
import time

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def main() -> None:
    banner("67 -- World Bank demographics and macro indicators")
    api = get_client()

    domain_id = None
    for arg in sys.argv[1:]:
        if arg.startswith("--domain-id"):
            domain_id = int(
                arg.split("=")[1] if "=" in arg
                else sys.argv[sys.argv.index(arg) + 1]
            )

    # ----------------------------------------------------------------
    # Step 1: Create or reuse a domain
    # ----------------------------------------------------------------
    if domain_id is None:
        step("1. Creating a throw-away domain for the demo")
        domain = api.domains.create(
            name="World Bank Demographics (67)",
            description=(
                "Macro/demographic indicators from the World Bank -- "
                "GDP, CPI inflation, and population growth for GBR and USA."
            ),
        )
        domain_id = domain["id"]
        print(f"  Domain ID: {domain_id}")
    else:
        step(f"1. Using existing domain {domain_id}")

    # ----------------------------------------------------------------
    # Step 2: Fetch GDP + CPI inflation for GBR and USA
    # ----------------------------------------------------------------
    step("2. Fetch GDP and CPI inflation (2015-2023) for GBR and USA")
    ds: dict = {}
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="worldbank",
            config={
                "indicators": ["NY.GDP.MKTP.CD", "FP.CPI.TOTL.ZG"],
                "countries": ["GBR", "USA"],
                "start_date": "2015",
                "end_date": "2023",
            },
        )
        print(f"  Status: {ds.get('status')}")
        print(f"  Dataset ID: {ds.get('id')}")
        print("  Columns: NY.GDP.MKTP.CD_GBR, NY.GDP.MKTP.CD_USA, "
              "FP.CPI.TOTL.ZG_GBR, FP.CPI.TOTL.ZG_USA")
    except AmbertraceError as e:
        print(f"  Fetch returned {e.code}: {e}")

    # ----------------------------------------------------------------
    # Step 3: Fetch population growth as a separate dataset
    # ----------------------------------------------------------------
    step("3. Fetch population growth (SP.POP.GROW) for GBR and USA")
    ds2: dict = {}
    try:
        ds2 = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="worldbank",
            config={
                "indicators": ["SP.POP.GROW"],
                "countries": ["GBR", "USA"],
                "start_date": "2015",
                "end_date": "2023",
            },
        )
        print(f"  Status: {ds2.get('status')}")
        print(f"  Dataset ID: {ds2.get('id')}")
    except AmbertraceError as e:
        print(f"  Fetch returned {e.code}: {e}")

    # ----------------------------------------------------------------
    # Step 4: Poll until datasets are ready
    # ----------------------------------------------------------------
    step("4. Polling until datasets are ready")
    for dataset_id in [ds.get("id"), ds2.get("id")]:
        if dataset_id is None:
            continue
        for _ in range(30):
            info = api.datasets.get(dataset_id)
            if info.get("status") in ("ready", "error"):
                break
            time.sleep(2)
        print(f"  Dataset {dataset_id}: status={info.get('status')}, "
              f"rows={info.get('row_count')}")

    # ----------------------------------------------------------------
    # Step 5: Show how this reaches Predictions as covariates
    # ----------------------------------------------------------------
    step("5. Covariates path to Predictions")
    print(
        "  Both datasets are now in the same domain. When you create a\n"
        "  PredictionConfig targeting one column (e.g. NY.GDP.MKTP.CD_GBR),\n"
        "  the Predictions pipeline automatically discovers all usable\n"
        "  datasets in the domain and uses the remaining columns as\n"
        "  covariates. No explicit dataset linking is needed.\n"
        "\n"
        "  Example:\n"
        "    api.prediction_configs.create(\n"
        "        domain_id=domain_id,\n"
        "        target_field='NY.GDP.MKTP.CD_GBR',\n"
        "        time_field='date',\n"
        "        horizon=1,\n"
        "    )\n"
        "  The CPI and population columns from both datasets are\n"
        "  automatically included as covariate features."
    )

    # ----------------------------------------------------------------
    # Step 6: Discover World Bank series via data search
    # ----------------------------------------------------------------
    step("6. Discover World Bank series via connector search")
    try:
        search = api.connectors.search(asset_class="economics/macro")
        wb_hits = [
            item for item in search["data"]
            if item.get("connector_type") == "worldbank"
        ]
        print(f"  World Bank hits for economics/macro: {len(wb_hits)} "
              f"(of {search['pagination']['total']} total)")
        for item in wb_hits[:5]:
            print(f"    {item['name']}: {item.get('description', '')[:80]}...")
    except AmbertraceError as e:
        print(f"  Search returned {e.code}: {e}")

    # ----------------------------------------------------------------
    # Cleanup
    # ----------------------------------------------------------------
    if "--domain-id" not in sys.argv:
        step("Cleaning up throw-away domain...")
        try:
            api.domains.delete(domain_id)
            print("  Deleted.")
        except AmbertraceError:
            print("  Cleanup skipped (domain may have active builds).")

    print(
        "\n  Done. World Bank data is licensed CC BY 4.0 -- "
        "attribution: Source: World Bank Open Data."
    )


if __name__ == "__main__":
    main()
