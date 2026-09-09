"""49 -- Multi-source panel with on_missing policy and transformation manifest.

Demonstrates the customer-controlled missing-value policy for wide multi-source
panels. When fetching data from multiple connectors, gaps arise from
source misalignment (different start dates, different cadences, discontinued
series). Without an explicit policy, gaps silently drop rows or NaN-pad,
collapsing a 40-year panel to a few years.

The ``on_missing`` parameter on ``datasets.fetch_multi()`` gives you declared
control:

  * ``{"method": "drop"}`` -- drop rows with any NaN (strictest).
  * ``{"method": "ffill"}`` -- forward-fill (last observation carried forward).
  * ``{"method": "interpolate", "max_gap": N}`` -- linear interpolation for
    short gaps only; longer gaps are dropped (prevents a 10-year gap from being
    silently interpolated).
  * ``{"method": "proxy_splice"}`` -- forward-fill + back-fill; fills ALL gaps
    but flags every filled cell as ``modeled_extrapolation: true`` in the
    transformation manifest.

After the merge, ``schema_info["transformation_manifest"]`` on the resulting
dataset records every fill/drop/interpolation with column, method,
rows_affected, and the modeled_extrapolation flag.

Usage:
    python 49_panel_on_missing_policy.py

Requires: AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL env vars.
For connectors that need keys (FRED): set the key on the platform or in the
connector config.
"""

from __future__ import annotations


from _common import api, print_section, wait_for_dataset

# ---- 1. Create a domain --------------------------------------------------
print_section("1. Create domain")
domain = api.domains.create(
    name="Panel Policy Demo",
    description="Demonstrates on_missing policy for multi-source panels",
)
print(f"Domain: {domain.id} ({domain.name})")

# ---- 2. Fetch a multi-source panel WITH on_missing -----------------------
print_section("2. Fetch multi-source panel with on_missing=interpolate")

# Example: two FRED sources with different history lengths.
# The on_missing policy controls how gaps from the outer join are handled.
ds = api.datasets.fetch_multi(
    domain_id=domain.id,
    sources=[
        {"connector_type": "fred", "config": {"series_ids": ["GS10", "GS2"]}},
        {"connector_type": "fred", "config": {"series_ids": ["DFF"]}},
    ],
    frequency="monthly",
    aggregation="last",
    on_missing={"method": "interpolate", "max_gap": 3},
)
print(f"Dataset: {ds['id']} (status={ds['status']})")

# ---- 3. Wait for the merge to complete -----------------------------------
print_section("3. Poll until ready")
ds = wait_for_dataset(api, ds["id"])
print(f"Status: {ds['status']}, rows={ds.get('row_count')}, cols={ds.get('column_count')}")

# ---- 4. Read the transformation manifest ---------------------------------
print_section("4. Transformation manifest")
schema = ds.get("schema_info") or {}
manifest = schema.get("transformation_manifest", [])
if manifest:
    for entry in manifest:
        col = entry.get("column", "?")
        method = entry.get("method", "?")
        rows = entry.get("rows_affected", 0)
        extrap = entry.get("modeled_extrapolation", False)
        flag = " [MODELED EXTRAPOLATION]" if extrap else ""
        print(f"  {col}: {method}, {rows} rows{flag}")
else:
    print("  (no transformations applied -- panel was already complete)")

# ---- 5. Check panel sufficiency -------------------------------------------
print_section("5. Panel sufficiency report")
report = api.datasets.panel_report(ds["id"])
print(f"  Usable rows: {report['intersection']['usable_rows']}")
print(f"  Coverage: {report['intersection']['coverage_pct']}%")
if report.get("stale_columns"):
    print(f"  Stale columns: {report['stale_columns']}")

# ---- 6. Compare policies -------------------------------------------------
print_section("6. Policy comparison (drop vs interpolate vs proxy_splice)")
print("  The on_missing policy controls the tradeoff between data quality")
print("  and data quantity. 'drop' is strictest (fewest rows, all observed).")
print("  'proxy_splice' is most permissive (most rows, but modeled_extrapolation")
print("  cells are flagged in the manifest).")
print()
print("  Use the panel_report + transformation_manifest together to understand")
print("  what your panel really contains before training.")

print_section("Done")
