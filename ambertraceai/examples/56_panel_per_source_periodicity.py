"""56 -- Multi-source panel: per-source periodicity via on_missing.per_column


Different sources behave differently when they go quiet, and ONE fill method
for the whole panel is often wrong for at least one of them:

  * A policy-rate / step-function series (e.g. an overnight rate that only
    changes at meetings) is correctly handled by ``ffill`` -- the rate really
    IS unchanged between meetings.
  * A smooth curve series (e.g. a bond yield or FX rate) is better handled by
    ``interpolate`` -- a straight line between two observed points is a much
    better estimate than "carry the old value forward" for a continuously
    moving series.

``on_missing.per_column`` lets you declare BOTH in the SAME panel:

    on_missing={
        "method": "ffill",              # top-level default for every OTHER column
        "per_column": {
            "fred__GS10": {"method": "interpolate", "max_gap": 2},
        },
    }

The named column(s) use their own method/max_gap; every other value column
keeps the top-level method. The transformation manifest records the ACTUAL
method applied to each column -- never merely the top-level default -- so you
can audit exactly what happened to every series.

Usage:
    python 56_panel_per_source_periodicity.py

Requires: AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL env vars.
For connectors that need keys (FRED): set the key on the platform or in the
connector config.
"""

from __future__ import annotations

from _common import banner, get_client, print_dataset, step, wait_for_dataset


def main() -> None:
    api = get_client()
    banner("Panel per-source periodicity via on_missing.per_column")

    domain = api.domains.create(
        name="Per-Source Periodicity Demo",
        description="Demonstrates mixed ffill/interpolate methods in one on_missing policy.",
    )
    step(f"Domain {domain['id']}: {domain['name']}")

    # DFF (Fed Funds Effective Rate) behaves like a step function -- ffill is
    # right for it. GS10 (10-Year Treasury yield) is a smooth curve -- give it
    # its OWN interpolate override so a short gap is linearly interpolated
    # instead of carried forward flat.
    dataset = api.datasets.fetch_multi(
        domain_id=domain["id"],
        sources=[
            {"connector_type": "fred", "config": {"series_ids": ["DFF"]}},
            {"connector_type": "fred", "config": {"series_ids": ["GS10"]}},
        ],
        frequency="monthly",
        aggregation="last",
        on_missing={
            "method": "ffill",  # top-level default -- applies to fred__DFF
            "per_column": {
                "fred__GS10": {"method": "interpolate", "max_gap": 2},
            },
        },
    )
    step(f"Dataset {dataset['id']} (status={dataset['status']})")

    dataset = wait_for_dataset(api, dataset["id"])
    print_dataset(dataset)

    schema = dataset.get("schema_info") or {}
    manifest = schema.get("transformation_manifest") or []

    print("\n  Per-column ACTUAL method (not merely the top-level default):")
    seen_columns = {m["column"] for m in manifest if m["column"] != "__all__"}
    for col in sorted(seen_columns):
        methods = sorted({m["method"] for m in manifest if m["column"] == col})
        print(f"    {col}: {methods}")

    print(
        "\n  fred__DFF used the top-level method (ffill); fred__GS10 used its "
        "own per_column override (interpolate) -- mixed in the SAME panel."
    )

    print("\n✓ Per-source periodicity walkthrough complete.")


if __name__ == "__main__":
    main()
