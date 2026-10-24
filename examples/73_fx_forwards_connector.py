"""73 -- FX forwards connector: CIP-derived 3M G4 forwards from FRED.

The ``fx_forwards`` connector computes 3-month outright forwards and forward
points for EURUSD, GBPUSD and USDJPY from FRED spot (H.10) and 3M interest
rates via covered interest parity:

    F = S * (1 + r_quote * 91/basis_quote) / (1 + r_base * 91/basis_base)

(ACT/360 for USD/EUR/JPY, ACT/365 for GBP; monthly EUR/GBP/JPY 3M rates are
forward-filled to the daily spot dates.) These are DERIVED forwards -- the fair
forward up to the cross-currency basis -- NOT market-observed quotes.

Output columns per pair: ``{PAIR}_3M`` (outright), ``{PAIR}_3M_PTS`` (forward
points; pips for EURUSD/GBPUSD, x100 for USDJPY) and, with ``output`` set,
``{PAIR}_SPOT`` / ``{PAIR}_3M_RATE_BASE`` / ``{PAIR}_3M_RATE_QUOTE``.

Bring your own free FRED key (https://fred.stlouisfed.org -> My Account -> API
Keys):
    FRED_API_KEY=your_fred_key

    python 73_fx_forwards_connector.py
"""

import sys

from _common import banner, fred_api_key, get_client, print_dataset, step, wait_for_dataset
from ambertraceai import AmbertraceError


def main() -> None:
    fred_key = fred_api_key()
    if not fred_key:
        sys.exit("Set FRED_API_KEY in examples/.env (free at https://fred.stlouisfed.org).")

    api = get_client()
    banner("FX forwards (CIP-derived, 3M, G4)")

    domain = api.domains.create(
        name="SDK Example — FX Forwards",
        description="3M EURUSD, GBPUSD and USDJPY forwards derived from FRED spot and rates.",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    try:
        dataset = api.datasets.fetch(
            domain_id=domain_id, connector_type="fx_forwards",
            config={
                "api_key": fred_key,
                "pairs": ["EURUSD", "GBPUSD", "USDJPY"],
                "tenor": "3M",
                "output": ["outright", "points", "spot"],
            },
        )
        dataset = wait_for_dataset(api, dataset["id"])
        print_dataset(dataset)
        cols = [c.get("name") for c in (dataset.get("schema_info") or {}).get("columns", [])]
        step(f"Columns: {cols}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
    finally:
        api.domains.delete(domain_id)
        step(f"Cleaned up domain #{domain_id}")

    print("\n✓ FX forwards walkthrough complete.")


if __name__ == "__main__":
    main()
