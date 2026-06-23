"""44 — Generic REST/CSV connector (bring-your-own-auth).

Ambertrace can ingest tabular data straight from an arbitrary HTTP endpoint via
the built-in ``rest`` connector. You point it at a URL that returns a flat array
of JSON objects (or a CSV body); Ambertrace fetches the URL *server-side* and
turns the response into a dataset. Any authentication is yours to supply — pass
it in the connector ``config`` (e.g. an ``Authorization`` header), since
Ambertrace does not hold third-party credentials on your behalf.

The three steps:
  1. Discover the ``rest`` connector via api.connectors.list() and print its
     required config fields.
  2. Create a domain to hold the ingested data.
  3. Fetch a dataset from a public, keyless JSON endpoint and print its shape.

The default endpoint (jsonplaceholder.typicode.com/users) is a public demo API
that returns a flat array of user objects — no key needed. Point --url at your
own endpoint and add --header "Authorization: Bearer ..." for authenticated APIs.

NOTE: the endpoint must be publicly reachable (Ambertrace fetches it from its
servers, not your machine). The endpoint or the rest connector may be
unavailable; the fetch is wrapped so the demo reports that cleanly.

Creates resources on your account (a domain + a dataset). Run with --help for
options.

    python 44_rest_connector.py
    python 44_rest_connector.py --url https://api.example.com/rows --header "Authorization: Bearer TOKEN"
"""

from __future__ import annotations

import argparse
from typing import Any

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    print_dataset,
    print_section,
    run_demo,
)

DEFAULT_URL = "https://jsonplaceholder.typicode.com/users"

DOMAIN_NAME = "REST Connector Ingestion"
DOMAIN_DESCRIPTION = "Ingests tabular data from an arbitrary REST/JSON endpoint"


def _parse_headers(pairs: list[str] | None) -> dict[str, str]:
    """Parse ``--header "Key: Value"`` pairs into a headers dict."""
    headers: dict[str, str] = {}
    for raw in pairs or []:
        key, sep, value = raw.partition(":")
        if not sep:
            raise SystemExit(f"Invalid --header (expected 'Key: Value'): {raw!r}")
        headers[key.strip()] = value.strip()
    return headers


def run_rest_connector(api, args: argparse.Namespace) -> None:
    total = 3

    print_section(1, total, "Discovering the 'rest' connector")
    connectors = api.connectors.list()
    rest = next(
        (c for c in connectors if (c.get("type") or c.get("name")) == "rest"),
        None,
    )
    if rest is None:
        print(f"  No 'rest' connector found among {len(connectors)} connector(s). "
              "It may be disabled on this deployment.")
    else:
        ctype = rest.get("type") or rest.get("name")
        print(f"  Connector '{ctype}': {rest.get('description', '')}")
        print(f"    Required config fields: {rest.get('requires') or []}")
        schema = rest.get("config_schema") or rest.get("schema")
        if schema:
            print(f"    Config schema: {schema}")
    print("\n  Bring-your-own-auth: pass credentials in the connector config, e.g.\n"
          '    config={"url": "https://api.example.com/rows",\n'
          '            "headers": {"Authorization": "Bearer <your-token>"}}')

    print_section(2, total, "Creating domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(3, total, "Fetching dataset from the REST endpoint")
    cfg: dict[str, Any] = {"url": args.url, "format": args.format}
    if args.records_path is not None:
        cfg["records_path"] = args.records_path
    headers = _parse_headers(args.header)
    if headers:
        cfg["headers"] = headers
    print(f"  GET {args.url} (format={args.format})")
    try:
        dataset = api.datasets.fetch(
            domain_id=domain["id"], connector_type="rest", config=cfg,
        )
        print_dataset(dataset)
        print(f"\nDone. Domain {domain['id']}, Dataset {dataset.get('id')}.")
    except AmbertraceError as exc:
        print(f"  ! REST fetch unavailable ({exc.status_code} {exc.code}): {exc}")
        print("    (The endpoint may be unreachable from Ambertrace's servers, or the "
              "'rest' connector may be disabled here.)")
        print(f"\nDone. Domain {domain['id']} created (no dataset ingested).")

    print("\n  This demo created a domain (and, on success, a dataset) on your account.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generic REST/CSV connector — bring-your-own-auth ingestion demo",
    )
    add_common_args(parser)
    parser.add_argument(
        "--url", default=DEFAULT_URL,
        help=f"Public endpoint returning a flat array of objects (default: {DEFAULT_URL}).",
    )
    parser.add_argument(
        "--format", default="json", choices=["json", "csv"],
        help="Response body format (default: json).",
    )
    parser.add_argument(
        "--records-path", default=None,
        help="Dotted path to the array of records inside a nested JSON body "
             "(default: the body itself is the array).",
    )
    parser.add_argument(
        "--header", action="append", default=None, metavar="KEY: VALUE",
        help='HTTP header to send (repeatable), e.g. --header "Authorization: Bearer TOKEN".',
    )
    args = parser.parse_args()
    run_demo(run_rest_connector, args)


if __name__ == "__main__":
    main()
