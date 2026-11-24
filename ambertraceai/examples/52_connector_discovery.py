"""52 -- Connector series-catalog discovery: find a series before you fetch it.

``api.connectors.discover(connector_type, **params)`` browses the catalog of
connectors that expose one:

* ``fred`` / ``fred_sentiment`` -- ``search_text=...`` (series search) or
  ``category_id=...`` (category browse; default is the root).  Needs your FRED
  key saved in your account.
* ``yahoo`` -- ``q=...`` symbol search.  Keyless.  Backed by Yahoo's
  UNOFFICIAL search endpoint, so it may change without notice.
* ``cftc`` -- ``report="disaggregated" | "legacy" | "financial"``: the
  commodity codes you can pass as ``commodity_codes``.  Keyless.
* ``eia`` -- ``route=...`` (see example 51).

Any other connector returns HTTP 422 ("does not support discovery").

    python 52_connector_discovery.py
"""

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def main() -> None:
    api = get_client()
    banner("Connector series-catalog discovery")

    try:
        quotes = api.connectors.discover("yahoo", q="crude oil")["quotes"]
        step(f"Yahoo 'crude oil': {[(q['symbol'], q['shortname']) for q in quotes[:5]]}")

        codes = api.connectors.discover("cftc", report="disaggregated")["codes"]
        gold = [c for c in codes if c["commodity_name"] == "GOLD"]
        step(f"CFTC disaggregated: {len(codes)} codes; GOLD -> {gold}")

        try:
            hits = api.connectors.discover("fred", search_text="interest rate")
            step(f"FRED 'interest rate': {[s['id'] for s in hits['series'][:5]]} "
                 f"of {hits['count']} matches")
            root = api.connectors.discover("fred")["categories"]
            step(f"FRED root categories: {[c['name'] for c in root[:5]]}")
        except AmbertraceError as e:
            step(f"FRED discovery needs your FRED key saved in your account: {e}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")

    print("\n  Discovery walkthrough complete.")


if __name__ == "__main__":
    main()
