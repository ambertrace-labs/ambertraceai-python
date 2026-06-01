"""03 — Connectors: discover external data sources.

Lists the available data-source connectors and their config requirements.
Connectors that hit third-party providers (e.g. FRED) need *your own* provider
API key, supplied in the ``config`` dict. Read-only — creates nothing.

    python 03_connectors.py
"""

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def main() -> None:
    api = get_client()
    banner("Connectors — discovery")

    connectors = api.connectors.list()
    step(f"{len(connectors)} connector(s) available:")
    for c in connectors:
        ctype = c.get("type") or c.get("name")
        requires = c.get("requires") or []
        desc = c.get("description", "")
        print(f"      • {ctype}: {desc} (requires: {requires})")

    # Optionally test a connector config. Most providers require credentials,
    # so we only attempt this if there's a no-auth connector available.
    if connectors:
        sample = connectors[0]
        ctype = sample.get("type") or sample.get("name")
        step(f"Attempting a config test for '{ctype}' (may require provider keys)…")
        try:
            result = api.connectors.test(connector_type=ctype, config={})
            step(f"Test result: rows={result.get('rows')} columns={result.get('columns')}")
        except AmbertraceError as e:
            step(f"Test rejected ({e.code}): {e}  — expected without provider config.")

    print("\n✓ Connector discovery complete.")


if __name__ == "__main__":
    main()
