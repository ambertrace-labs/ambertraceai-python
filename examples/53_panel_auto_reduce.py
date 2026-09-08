"""53 -- Customer-controlled panel construction: column roles + auto-reduce.

Demonstrates auto-reduce: instead of a manual drop-column-and-retry loop
when a declared sufficiency bar (``min_rows`` / ``min_history_years``) is
unmet, tag panel columns by ROLE --

  * ``core_columns`` -- must NEVER be dropped (the target and, in timeseries
    mode, the time index are implicitly core regardless of this list).
  * everything else -- AUXILIARY, droppable, sparsest (most nulls) first.

...and set ``auto_reduce=True``. At :meth:`train` time, if the raw panel
falls short of ``min_rows``, the sparsest auxiliary columns are dropped ONE
AT A TIME (never a core column, never by filling/fabricating a value --
columns are removed, nothing is imputed) until the bar is met. The exact
dropped columns + before/after usable-row counts come back as a
``reduction_manifest`` on the 202 train response AND are readable back on
the config afterwards.

If the bar is UNREACHABLE even after dropping every auxiliary column, the
platform still returns the structured HTTP 409 ``sufficiency_gate_failed``
(with the attempted cut recorded under ``auto_reduce_attempted``) -- this
never trains on a sub-bar panel.

Usage:
    python 53_panel_auto_reduce.py

Requires: AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL env vars.
"""

from __future__ import annotations

import csv
import tempfile
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import banner, build_ontology, build_platform, get_client, print_dataset, step

# A synthetic cross-sectional panel: 30 rows, a dense target + core column,
# and three AUXILIARY columns of KNOWN, increasing sparsity (aux_a: 2 nulls,
# aux_b: 10 nulls, aux_c: 22 nulls). The all-columns intersection therefore
# tops out well under 30 usable rows -- exactly the shape that motivates
# auto-reduce.
N_ROWS = 30
AUX_C_NULLS = 22  # sparsest -- dropped first
AUX_B_NULLS = 10
AUX_A_NULLS = 2


def _write_panel_csv() -> Path:
    tmp = Path(tempfile.mkstemp(suffix=".csv")[1])
    with tmp.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["target_yield", "core_signal", "aux_a", "aux_b", "aux_c"])
        for i in range(N_ROWS):
            row = [
                round(1.0 + 0.01 * i, 4),   # target_yield -- always present
                round(0.5 + 0.02 * i, 4),   # core_signal -- always present (core)
                "" if i < AUX_A_NULLS else round(0.1 * i, 4),
                "" if i < AUX_B_NULLS else round(0.2 * i, 4),
                "" if i < AUX_C_NULLS else round(0.3 * i, 4),
            ]
            writer.writerow(row)
    return tmp


def main() -> None:
    api = get_client()
    banner("Panel auto-reduce -- column roles + declared sufficiency bar")

    csv_path = _write_panel_csv()
    step(f"Wrote synthetic panel: {csv_path} ({N_ROWS} rows)")

    domain = api.domains.create(
        name="Panel Auto-Reduce Demo",
        description="Synthetic cross-sectional panel with sparse auxiliary columns.",
    )
    step(f"Domain {domain['id']}: {domain['name']}")

    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(csv_path))
    print_dataset(dataset)

    domain = build_ontology(api, domain["id"])
    platform = build_platform(api, domain["id"], dataset["id"])
    step(f"Platform {platform['id']} ({platform.get('status')})")

    # Declare a row bar that the RAW all-columns intersection cannot meet
    # (only 30 - 22 = 8 rows survive with aux_c present), but that dropping
    # aux_c alone DOES meet (30 - 10 = 20 rows once aux_b is also gone is
    # more than needed; dropping just the sparsest column, aux_c, already
    # gets to 30 - 10 = 20... we ask for 25, which additionally requires
    # dropping aux_b too, exercising a MULTI-column reduction).
    config_id = None
    try:
        config = api.predictions.create_config(
            platform["id"],
            mode="cross_sectional",
            target_field="target_yield",
            core_columns=["core_signal"],   # never dropped, even if sparse
            auto_reduce=True,
            min_rows=25,
        )
        config_id = config["id"]
        step(f"Config {config_id}: core_columns={config.get('core_columns')}, "
             f"auto_reduce={config.get('auto_reduce')}, min_rows={config.get('min_rows')}")

        # wait=False to inspect the raw 202 body (carries reduction_manifest
        # directly, before polling the job to completion).
        resp = api.predictions.train(platform["id"], config_id, wait=False)
        step(f"Train 202: status={resp.get('status')}, job_id={resp.get('job_id')}")

        manifest = resp.get("reduction_manifest")
        if manifest:
            print("\n  Reduction manifest:")
            for entry in manifest.get("dropped_columns", []):
                print(f"    dropped {entry['column']!r} "
                      f"(null_count={entry['null_count']}, action={entry['action']})")
            print(f"    usable_rows: {manifest['usable_rows_before']} -> "
                  f"{manifest['usable_rows_after']} (target {manifest['target_rows']})")
        else:
            print("  (no reduction needed -- the declared bar was already met)")

        api.wait_for_job(resp["job_id"], what="Training")
        trained = next(
            (c for c in api.predictions.list_configs(platform["id"]) if c["id"] == config_id),
            None,
        )
        if trained:
            step(f"Training finished: status={trained.get('status')}, "
                 f"feature_fields={trained.get('feature_fields')}")
            # Also readable back on the config after the job settles.
            print(f"  config.reduction_manifest: {trained.get('reduction_manifest')}")

    except AmbertraceError as e:
        # An UNREACHABLE bar (e.g. min_rows > 30) still 409s -- fail-closed,
        # never trains on a sub-bar panel. Try setting min_rows=100 above to
        # see this branch (auto_reduce_attempted names the attempted cut).
        print(f"\n  ! sufficiency_gate_failed ({e.status_code}): {e}")
    finally:
        if config_id is not None:
            api.predictions.delete_config(platform["id"], config_id)
            step(f"Deleted config #{config_id}")
        csv_path.unlink(missing_ok=True)

    print("\n✓ Panel auto-reduce walkthrough complete.")


if __name__ == "__main__":
    main()
