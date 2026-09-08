"""54 -- Multi-source panel with on_stale policy for discontinued series.

Demonstrates the customer-controlled staleness policy for wide multi-source
panels. When one source stops publishing (e.g. a discontinued FRED series),
the outer join forward-fills with NaN -- but the series is STALE, not just
missing. The ``on_stale`` parameter on ``datasets.fetch_multi()`` controls
what happens when stale columns are detected:

  * ``{"action": "warn"}`` -- proceed (default); staleness is recorded in the
    panel sufficiency report (``stale_columns``) but does not block.
  * ``{"action": "error"}`` -- mark the dataset as error; the error message
    names the stale columns and suggests alternatives.
  * ``{"action": "drop_columns"}`` -- drop stale columns from the merged frame,
    re-derive schema, and record the dropped columns as
    ``dropped_stale_columns`` on schema_info.

The ``stale_periods`` parameter (default 3) controls the threshold: a column
is flagged stale when its last non-null value lags the panel's last index by
MORE than ``stale_periods`` cadence periods (cadence = median index spacing).

Combine with ``on_missing`` for full panel construction control:
``on_missing`` handles NaN cells from the outer join; ``on_stale`` handles
columns that stopped publishing entirely.

Usage:
    python 54_panel_on_stale_policy.py

Requires: AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL env vars.
For connectors that need keys (FRED): set the key on the platform or in the
connector config.
"""

from __future__ import annotations


from _common import api, print_section, wait_for_dataset

# ---- 1. Create a domain --------------------------------------------------
print_section("1. Create domain")
domain = api.domains.create(
    name="Stale Policy Demo",
    description="Demonstrates on_stale policy for discontinued series",
)
print(f"Domain: {domain.id} ({domain.name})")

# ---- 2. Fetch with on_stale='drop_columns' --------------------------------
print_section("2. Fetch multi-source panel with on_stale=drop_columns")

# Two FRED sources. If one series is discontinued, on_stale controls the
# action. 'drop_columns' removes the stale series and keeps the full panel.
ds = api.datasets.fetch_multi(
    domain_id=domain.id,
    sources=[
        {"connector_type": "fred", "config": {"series_ids": ["GS10", "GS2"]}},
        {"connector_type": "fred", "config": {"series_ids": ["DFF"]}},
    ],
    frequency="monthly",
    aggregation="last",
    on_missing={"method": "ffill"},
    on_stale={"action": "drop_columns", "stale_periods": 3},
)
print(f"Dataset: {ds['id']} (status={ds['status']})")

# ---- 3. Wait for the merge to complete -----------------------------------
print_section("3. Poll until ready (or error)")
ds = wait_for_dataset(api, ds["id"])
print(f"Status: {ds['status']}, rows={ds.get('row_count')}, cols={ds.get('column_count')}")

# ---- 4. Check for dropped stale columns ----------------------------------
print_section("4. Dropped stale columns")
schema = ds.get("schema_info") or {}
dropped = schema.get("dropped_stale_columns", [])
if dropped:
    print(f"  Stale columns dropped: {dropped}")
else:
    print("  (no stale columns detected -- all sources are current)")

# ---- 5. Check panel sufficiency after drops --------------------------------
print_section("5. Panel sufficiency report (post-drop)")
report = api.datasets.panel_report(ds["id"])
print(f"  Usable rows: {report['intersection']['usable_rows']}")
print(f"  Coverage: {report['intersection']['coverage_pct']}%")
if report.get("stale_columns"):
    print(f"  Still stale: {report['stale_columns']}")
else:
    print("  No stale columns remain (dropped or none detected)")

# ---- 6. Policy comparison ------------------------------------------------
print_section("6. Policy comparison")
print("  on_stale={'action': 'warn'}       -- proceed, staleness in report only")
print("  on_stale={'action': 'error'}       -- fail the dataset, name the columns")
print("  on_stale={'action': 'drop_columns'} -- remove stale columns, keep full panel")
print()
print("  Use stale_periods to control the threshold (default 3 cadence periods).")
print("  Combine with on_missing for full panel construction control.")

print_section("Done")
