"""19 -- Data Search: resolve NL data requests to concrete series.

Demonstrates the agent workflow for the instruction:

    'build me a model of 5y german rate, using economic data,
     asian equities, developed-market FX'

Each clause maps to a structured search call via
``api.connectors.search(...)``:

  (a) '5y german rate'       -> asset_class=rates, region=eurozone, tenor=5Y
      NOTE: euro-area sovereign yield curves are tagged country='EA', not
      'DE' -- use region='eurozone' (which includes EA) instead of
      country='DE' to find German/euro-area rates.
  (b) 'economic data'        -> asset_class=economics/macro
  (c) 'asian equities'       -> asset_class=equities, region=asia
  (d) 'developed-market FX'  -> asset_class=fx, region=developed-markets

Supported filters:
  - Structured: asset_class, country, region, currency, tenor
  - Free-text (q=): lexical substring match on names/descriptions
  - Region groups: asia, europe, americas, developed-markets,
    emerging-markets, G7, G10, eurozone
  - Pagination: offset, limit

Results include both connector-level and series-level entries.
Series-level entries cover the statically-enumerable set (ECB yield
curves, BoE gilts, FRED DGS rates and common macro indicators).

    python 19_data_search.py
"""

from _common import banner, get_client, step


def main() -> None:
    api = get_client()
    banner("Data Search -- agent-driven data resolution")

    # (a) 5Y German rate -> eurozone rates with 5Y tenor.
    # Euro-area curves are tagged EA (not DE), so region=eurozone is the
    # correct decomposition -- country=DE would return empty.
    step("(a) Resolve '5y german rate'")
    resp_a = api.connectors.search(
        asset_class="rates", region="eurozone", tenor="5Y",
    )
    print(f"  Found {resp_a['pagination']['total']} results")
    for item in resp_a["data"][:3]:
        print(f"    [{item['level']}] {item['connector_type']}/{item['name']}: {item['description']}")

    # (b) Economic data
    step("(b) Resolve 'economic data'")
    resp_b = api.connectors.search(asset_class="economics/macro")
    print(f"  Found {resp_b['pagination']['total']} results")
    connectors = {item["connector_type"] for item in resp_b["data"]}
    print(f"  Connector types: {sorted(connectors)}")

    # (c) Asian equities
    step("(c) Resolve 'asian equities'")
    resp_c = api.connectors.search(asset_class="equities", region="asia")
    print(f"  Found {resp_c['pagination']['total']} results")
    for item in resp_c["data"]:
        print(f"    [{item['level']}] {item['connector_type']}: {item['description']}")

    # (d) Developed-market FX
    step("(d) Resolve 'developed-market FX'")
    resp_d = api.connectors.search(asset_class="fx", region="developed-markets")
    print(f"  Found {resp_d['pagination']['total']} results")
    for item in resp_d["data"]:
        print(f"    [{item['level']}] {item['connector_type']}: {item['description']}")

    # Bonus: free-text search
    step("Free-text search: 'treasury'")
    resp_q = api.connectors.search(q="treasury")
    print(f"  Found {resp_q['pagination']['total']} results matching 'treasury'")
    for item in resp_q["data"][:5]:
        tenor_str = f" (tenor={item['tenor']})" if item.get("tenor") else ""
        print(f"    {item['name']}: {item['description']}{tenor_str}")

    print("\nDone.")


if __name__ == "__main__":
    main()
