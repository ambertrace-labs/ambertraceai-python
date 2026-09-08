"""03 -- Connectors: discover, filter, and browse external data sources.

Lists the available data-source connectors with their config requirements and
taxonomy metadata (asset classes, countries, currencies). Supports filtering
by ``asset_class``, ``country``, and ``currency`` query parameters.

**Agent workflow:** an agent can browse connectors by metadata to
find the right data source for a task:

  1. List all connectors to see what is available.
  2. Filter by asset_class/country/currency to narrow to relevant sources.
  3. Inspect config_schema to learn what config keys each connector needs.
  4. Use ``api.connectors.search(...)`` (see ``19_data_search.py``) to
     find specific series within a connector's catalog.
  5. validate_only=True to dry-run a config before fetching.

Connectors that hit third-party providers (e.g. FRED) need *your own* provider
API key, supplied in the ``config`` dict. Read-only -- creates nothing.

    python 03_connectors.py
"""

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def main() -> None:
    api = get_client()
    banner("Connectors -- discovery and filtering")

    # --- 1. List all connectors with taxonomy metadata ----------------------
    connectors = api.connectors.list()
    step(f"{len(connectors)} connector(s) available:")
    for c in connectors:
        ctype = c.get("type") or c.get("name")
        requires = c.get("requires") or []
        classes = c.get("asset_classes") or []
        countries = c.get("countries") or []
        currencies = c.get("currencies") or []
        desc = c.get("description", "")
        print(f"      {ctype}: {desc}")
        print(f"        requires: {requires}")
        print(f"        asset_classes: {classes}  countries: {countries}  currencies: {currencies}")
        print(f"        redistributable: {c.get('redistributable')}  entitlement: {c.get('entitlement')}")

    # --- 2. Filter by asset class -------------------------------------------
    step("Filtering connectors by asset_class='rates'...")
    rates = api.connectors.list(asset_class="rates")
    step(f"  {len(rates)} rate connector(s): {[c['type'] for c in rates]}")

    # --- 3. Filter by country -----------------------------------------------
    step("Filtering connectors by country='GB'...")
    gb = api.connectors.list(country="GB")
    step(f"  {len(gb)} GB connector(s): {[c['type'] for c in gb]}")

    # --- 4. Filter by currency ----------------------------------------------
    step("Filtering connectors by currency='EUR'...")
    eur = api.connectors.list(currency="EUR")
    step(f"  {len(eur)} EUR connector(s): {[c['type'] for c in eur]}")

    # --- 5. Combined filter -------------------------------------------------
    step("Filtering connectors by asset_class='rates', country='GB', currency='GBP'...")
    gb_rates = api.connectors.list(asset_class="rates", country="GB", currency="GBP")
    step(f"  {len(gb_rates)} GB rates connector(s): {[c['type'] for c in gb_rates]}")

    # --- 6. Inspect config_schema for agent-driven configuration -----
    # An agent can read config_schema to learn WHAT to configure before calling
    # test() or fetch(). Each field has: name, type, required, description,
    # and optionally default/enum/example.
    step("Inspecting config_schema for programmatic connector setup...")
    for c in connectors[:3]:
        ctype = c.get("type") or c.get("name")
        schema = c.get("config_schema") or []
        if schema:
            print(f"  {ctype}: {len(schema)} config field(s)")
            for field in schema:
                req = "REQUIRED" if field.get("required") else "optional"
                print(f"    {field['name']} ({field['type']}, {req}): {field['description']}")
        else:
            print(f"  {ctype}: no config schema declared")

    # --- 7. Cross-reference: search series within a connector's catalog ------
    # Use data/search to find series-level entries for a specific connector,
    # then build the connector config from the search results.
    step("Agent workflow: find ECB series via search, then build config...")
    ecb_series = api.connectors.search(
        asset_class="rates", country="EA", tenor="5Y",
    )
    if ecb_series["data"]:
        series_names = [
            item["name"] for item in ecb_series["data"]
            if item["level"] == "series" and item["connector_type"] == "ecb"
        ]
        print(f"  Found {len(series_names)} ECB 5Y series: {series_names[:3]}")
        if series_names:
            print(f"  -> connector config: {{'series_keys': {series_names[:2]}}}")

    # --- 8. Test a connector (optional) -------------------------------------
    if connectors:
        sample = connectors[0]
        ctype = sample.get("type") or sample.get("name")
        step(f"Attempting a config test for '{ctype}' (may require provider keys)...")
        try:
            result = api.connectors.test(connector_type=ctype, config={})
            step(f"Test result: rows={result.get('rows')} columns={result.get('columns')}")
        except AmbertraceError as e:
            step(f"Test rejected ({e.code}): {e}  -- expected without provider config.")

    # --- 9. validate_only: check a config WITHOUT fetching -------------------
    # An ASYNC connector (one that fetches in the background) cannot be tested
    # inline -- a plain test() returns 422.  validate_only=True checks the
    # config only, and works for every connector including the async ones.
    step("Validating an async connector's config with validate_only=True...")
    check = api.connectors.test(
        connector_type="boe_yield_curves",
        config={"curve_types": ["nominal"], "max_backfill_archives": 2},
        validate_only=True,
    )
    step(f"  valid={check.get('valid')} errors={check.get('errors')}")

    # The same call with a bad config reports WHY, without any network fetch.
    bad = api.connectors.test(
        connector_type="boe_yield_curves",
        config={"curve_types": ["not_a_curve"]},
        validate_only=True,
    )
    step(f"  bad config -> valid={bad.get('valid')} errors={bad.get('errors')}")

    print("\nConnector discovery complete.")


if __name__ == "__main__":
    main()
