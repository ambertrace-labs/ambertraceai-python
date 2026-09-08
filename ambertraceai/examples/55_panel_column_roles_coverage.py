"""55 -- Multi-source panel: column roles (ask 2) + coverage filter (ask 4).

Two related policies, composed on ``datasets.fetch_multi()``:

  * ``column_roles`` -- tag POST-NAMESPACE columns as ``"core"`` (never
    dropped by any downstream policy) or ``"auxiliary"`` (droppable).
    Columns you don't list default to ``"auxiliary"``.
  * ``require_coverage`` -- drop AUXILIARY columns whose non-null coverage
    falls below a declared ``min_pct``, measured either against the whole
    panel (``relative_to="panel"``, default) or against the rows where every
    CORE column is non-null (``relative_to="core"``).

The pipeline order is: merge -> on_stale -> require_coverage -> on_missing ->
panel_report. require_coverage runs on the RAW (pre-fill) frame, so a sparse
auxiliary series is dropped BEFORE it gets forward-filled into looking dense.

CORE columns are structurally exempt from require_coverage AND from
on_stale's ``drop_columns`` action -- a stale/low-coverage CORE column is a
dataset error, never a silent drop (see ``56_panel_per_source_periodicity.py``
sibling example and ``54_panel_on_stale_policy.py`` for the on_stale side).

Usage:
    python 55_panel_column_roles_coverage.py

Requires: AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL env vars.
For connectors that need keys (FRED): set the key on the platform or in the
connector config.
"""

from __future__ import annotations

from _common import banner, get_client, print_dataset, step, wait_for_dataset


def main() -> None:
    api = get_client()
    banner("Panel column roles + coverage filter")

    domain = api.domains.create(
        name="Column Roles + Coverage Demo",
        description="Demonstrates column_roles and require_coverage on a multi-source panel.",
    )
    step(f"Domain {domain['id']}: {domain['name']}")

    # Two FRED sources. Declare the primary rate series as CORE (never
    # dropped); everything else defaults to auxiliary. require_coverage then
    # drops any auxiliary series below 70% coverage -- catching a sparse or
    # short-lived series BEFORE it gets forward-filled into looking healthy.
    dataset = api.datasets.fetch_multi(
        domain_id=domain["id"],
        sources=[
            {"connector_type": "fred", "config": {"series_ids": ["GS10"]}},
            {"connector_type": "fred", "config": {"series_ids": ["DFF", "T10Y2Y"]}},
        ],
        frequency="monthly",
        aggregation="last",
        column_roles={"fred__GS10": "core"},
        require_coverage={"relative_to": "panel", "min_pct": 70.0},
        on_missing={"method": "ffill"},
    )
    step(f"Dataset {dataset['id']} (status={dataset['status']})")

    dataset = wait_for_dataset(api, dataset["id"])
    print_dataset(dataset)

    schema = dataset.get("schema_info") or {}

    print("\n  column_roles persisted on schema_info:")
    print(f"    {schema.get('column_roles')}")

    dropped = schema.get("coverage_filter_dropped") or []
    if dropped:
        print("\n  Coverage filter dropped:")
        for entry in dropped:
            print(
                f"    {entry['column']}: {entry['coverage_pct']}% "
                f"< {entry['threshold']}% (relative_to={entry['relative_to']})"
            )
    else:
        print("\n  No auxiliary column fell below the coverage threshold.")

    col_names = [c["name"] for c in schema.get("columns") or []]
    print(f"\n  Surviving columns: {col_names}")
    print("  (fred__GS10 is CORE -- it is guaranteed present regardless of coverage)")

    # The panel report's per-column 'role' field mirrors the same declaration
    # PanelColumnOut.role is 'core'/'auxiliary'/None.
    report = api.datasets.panel_report(dataset["id"])
    print("\n  Panel report roles:")
    for col in report.get("columns") or []:
        print(f"    {col['name']}: role={col.get('role')}")

    print("\n✓ Column roles + coverage filter walkthrough complete.")


if __name__ == "__main__":
    main()
