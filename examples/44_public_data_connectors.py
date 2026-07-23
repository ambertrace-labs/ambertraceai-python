"""44 -- Public data connectors: ingest macro/economic data from six new sources.

Demonstrates the six public-data connectors added in 1.0.9:

    * ``eurostat``   -- EU macro/prices/labour (Eurostat SDMX, no API key)
    * ``fiscaldata`` -- US Treasury debt, rates, FX (FiscalData API, no API key)
    * ``edgar``      -- SEC EDGAR XBRL company fundamentals (no API key)
    * ``imf``        -- IMF iData global macro (SDMX, BYO API key)
    * ``worldbank``  -- World Bank development indicators (no API key)
    * ``fred`` with ALFRED vintage -- point-in-time snapshots for honest backtests

Each section shows (1) how to call ``api.datasets.fetch`` with the connector's
config, (2) which config fields are required, and (3) how to merge multiple
sources into one date-aligned panel with ``api.datasets.fetch_multi``.

Prerequisites:
    * ``AMBERTRACE_API_KEY`` -- your Ambertrace API key (see examples/.env).
    * ``FRED_API_KEY`` -- a free FRED key (https://fred.stlouisfed.org) for
      the FRED/ALFRED section.
    * ``IMF_API_KEY`` -- an IMF iData subscription key
      (Ocp-Apim-Subscription-Key) for the IMF section. Sign up at
      https://idata.imf.org. Set the env var; never hard-code it.

    python 44_public_data_connectors.py [--domain-id N]
"""

from __future__ import annotations

import os
import sys

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


# ---------------------------------------------------------------------------
# Env helpers -- bring-your-own-key connectors read keys from the environment.
# ---------------------------------------------------------------------------

def _fred_key() -> str | None:
    return os.environ.get("FRED_API_KEY")


def _imf_key() -> str | None:
    return os.environ.get("IMF_API_KEY")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    api = get_client()
    banner("Public Data Connectors")

    # --- 0. Discover available connectors -----------------------------------
    step("Listing all available connectors...")
    connectors = api.connectors.list()
    for c in connectors:
        ctype = c.get("type") or c.get("name")
        requires = c.get("requires") or []
        desc = c.get("description", "")
        print(f"      {ctype}: {desc}")
        if requires:
            print(f"        requires: {requires}")

    # We need a domain to attach datasets. Create a throw-away one, or use the
    # --domain-id flag if the caller already has one.
    domain_id: int | None = None
    for i, arg in enumerate(sys.argv):
        if arg == "--domain-id" and i + 1 < len(sys.argv):
            domain_id = int(sys.argv[i + 1])
    if domain_id is None:
        domain = api.domains.create(
            name="Connector Demo (44)",
            description="Throw-away domain for the public-data-connectors example",
        )
        domain_id = domain["id"]
        step(f"Created throw-away domain {domain_id}")
    else:
        step(f"Using existing domain {domain_id}")

    # --- 1. Eurostat -- EU HICP (no API key) --------------------------------
    print("\n--- Eurostat (EU HICP, no API key) ---")
    step("Fetching EU HICP index from Eurostat SDMX...")
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="eurostat",
            config={
                "dataset": "prc_hicp_midx",
                "key": "M.I15.CP00.EU27_2020",
                "label": "HICP",
            },
        )
        step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"Eurostat fetch returned {e.code}: {e}")

    # --- 2. FiscalData -- US Treasury avg interest rates (no API key) --------
    print("\n--- US Treasury FiscalData (avg interest rates, no API key) ---")
    step("Fetching average interest rates from FiscalData...")
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="fiscaldata",
            config={
                "endpoint": "v2/accounting/od/avg_interest_rates",
                "fields": [
                    "record_date",
                    "security_desc",
                    "avg_interest_rate_amt",
                ],
                "pivot_column": "security_desc",
                "value_column": "avg_interest_rate_amt",
                "label": "rates",
            },
        )
        step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"FiscalData fetch returned {e.code}: {e}")

    # --- 3. SEC EDGAR XBRL -- company fundamentals (no API key) -------------
    print("\n--- SEC EDGAR XBRL (AAPL revenue + assets, no API key) ---")
    step("Fetching AAPL annual revenue and assets from SEC EDGAR...")
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="edgar",
            config={
                "tickers": ["AAPL"],
                "concepts": [
                    "RevenueFromContractWithCustomerExcludingAssessedTax",
                    "Assets",
                ],
                "period": "annual",
            },
        )
        step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"EDGAR fetch returned {e.code}: {e}")

    # --- 4. IMF iData SDMX -- US CPI (BYO API key) -------------------------
    imf_key = _imf_key()
    print("\n--- IMF iData SDMX (US CPI, BYO API key) ---")
    if imf_key:
        step("Fetching US CPI from IMF iData SDMX (agency-qualified dataflow)...")
        try:
            ds = api.datasets.fetch(
                domain_id=domain_id,
                connector_type="imf",
                config={
                    "dataflow": "IMF.STA,CPI",
                    "key": "USA.CPI._T.IX.M",
                    "api_key": imf_key,
                    "label": "CPI",
                },
            )
            step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
        except AmbertraceError as e:
            step(f"IMF fetch returned {e.code}: {e}")
    else:
        step(
            "Skipped -- set IMF_API_KEY (Ocp-Apim-Subscription-Key) to run. "
            "Sign up at https://idata.imf.org"
        )

    # --- 5. World Bank -- GDP + CPI for GBR and USA (no API key) ------------
    print("\n--- World Bank Open Data (GDP + CPI, no API key) ---")
    step("Fetching GDP and CPI for GBR and USA from the World Bank...")
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="worldbank",
            config={
                "indicators": ["NY.GDP.MKTP.CD", "FP.CPI.TOTL.ZG"],
                "countries": ["GBR", "USA"],
            },
        )
        step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"World Bank fetch returned {e.code}: {e}")

    # --- 6. FRED + ALFRED vintage -- point-in-time snapshot (BYO key) -------
    fred_key = _fred_key()
    print("\n--- FRED ALFRED vintage (point-in-time snapshot, BYO key) ---")
    if fred_key:
        step(
            "Fetching GS10 (10y yield) as it was known on 2024-06-30 "
            "(ALFRED as_of_date -- avoids look-ahead bias in backtests)..."
        )
        try:
            ds = api.datasets.fetch(
                domain_id=domain_id,
                connector_type="fred",
                config={
                    "series_ids": ["GS10"],
                    "api_key": fred_key,
                    "as_of_date": "2024-06-30",
                },
            )
            step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
        except AmbertraceError as e:
            step(f"FRED ALFRED fetch returned {e.code}: {e}")
    else:
        step(
            "Skipped -- set FRED_API_KEY to run. "
            "Get a free key at https://fred.stlouisfed.org"
        )

    # --- 7. Multi-source merge -- combine connectors in one dataset ---------
    print("\n--- Multi-source fetch (Eurostat + World Bank, merged) ---")
    step(
        "Merging Eurostat HICP + World Bank GDP into one date-aligned panel "
        "via fetch_multi..."
    )
    try:
        ds = api.datasets.fetch_multi(
            domain_id=domain_id,
            sources=[
                {
                    "connector_type": "eurostat",
                    "config": {
                        "dataset": "prc_hicp_midx",
                        "key": "M.I15.CP00.EU27_2020",
                        "label": "HICP",
                    },
                },
                {
                    "connector_type": "worldbank",
                    "config": {
                        "indicators": ["NY.GDP.MKTP.CD"],
                        "countries": ["USA"],
                    },
                },
            ],
            frequency="monthly",
            aggregation="last",
        )
        step(f"Merged dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"fetch_multi returned {e.code}: {e}")

    # --- 8. DTCC swap curves -- OIS rates for USD/GBP (no API key) -----------
    # Output columns are named ``{currency}_{tenor}`` -- e.g. ``USD_10Y``,
    # ``GBP_5Y``.  Each column holds the aggregated OIS swap rate (decimal,
    # e.g. 0.0418 = 4.18%) for that currency-tenor pair, one row per date.
    # Use these column names as ``target_field`` in the prediction pipeline
    # (e.g. ``target_field="USD_10Y"`` to forecast the 10-year USD SOFR rate).
    print("\n--- DTCC swap curves (OIS rates, no API key) ---")
    step(
        "Fetching OIS swap-rate curves (SOFR/SONIA) from DTCC PPD -- "
        "trade-level public data curated into a clean curve..."
    )
    try:
        ds = api.datasets.fetch(
            domain_id=domain_id,
            connector_type="swap_curves",
            config={
                "currencies": ["USD", "GBP"],
                "tenors": ["2Y", "5Y", "10Y", "30Y"],
                "method": "median",
                "max_backfill_days": 5,
            },
        )
        step(f"Dataset {ds.get('id')}: status={ds.get('status')}")
    except AmbertraceError as e:
        step(f"Swap curves fetch returned {e.code}: {e}")

    # --- Cleanup (throw-away domain) ----------------------------------------
    if "--domain-id" not in sys.argv:
        step(f"Cleaning up throw-away domain {domain_id}...")
        try:
            api.domains.delete(domain_id)
            step("Deleted.")
        except AmbertraceError:
            step("Cleanup skipped (domain may have active builds).")

    print("\nDone. Each fetch is async -- poll api.datasets.get(id) until "
          "status='ready' before building on it.")


if __name__ == "__main__":
    main()
