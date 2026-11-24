"""84 — Job management: list in-flight jobs, cancel one, launch fresh, re-trigger.

A long-running forecast is a background job. Re-sending an identical request while it is in
flight re-attaches to the SAME job (``deduplicated=True``). To take control of it:

  1. ``predictions.symbolic_forecast(..., wait=False)`` -- launch and get the job id back.
  2. Send the identical request again -- you get the SAME job id (deduplicated).
  3. ``jobs.list(status="pending,running", ...)`` -- see what is in flight on the platform.
  4. ``jobs.cancel(job_id)`` -- stop it (it becomes ``failed`` / "Cancelled by user.").
  5. ``symbolic_forecast(..., force_new=True)`` -- always start a fresh run (re-trigger).
  6. ``wait_for_job`` -- collect the forecast from the fresh job.

    python 84_job_management.py --platform-id 12 --config-id 3
"""

from __future__ import annotations

import argparse

from _common import add_common_args, print_section, run_demo


def run_job_management(api, args: argparse.Namespace) -> None:
    total = 6
    pid, cid = args.platform_id, args.config_id

    print_section(1, total, "Launch a forecast without waiting")
    first = api.predictions.symbolic_forecast(pid, prediction_config_id=cid, wait=False)
    print(f"  Job {first['job_id']} deduplicated={first['deduplicated']}")

    print_section(2, total, "An identical request re-attaches to the same job")
    again = api.predictions.symbolic_forecast(pid, prediction_config_id=cid, wait=False)
    print(f"  Job {again['job_id']} deduplicated={again['deduplicated']}")

    print_section(3, total, "List the platform's in-flight jobs")
    live = api.jobs.list(status="pending,running", type="symbolic_forecast",
                         ref_type="platform", ref_id=pid)
    for job in live:
        print(f"  Job {job['id']} {job['status']} step={job['step']}")

    print_section(4, total, "Cancel the stalled job")
    cancelled = api.jobs.cancel(first["job_id"])
    print(f"  Job {cancelled['id']} -> {cancelled['status']}: {cancelled['error_message']}")

    print_section(5, total, "Re-trigger: launch a fresh job with force_new=True")
    fresh = api.predictions.symbolic_forecast(
        pid, prediction_config_id=cid, force_new=True, wait=False)
    print(f"  New job {fresh['job_id']} deduplicated={fresh['deduplicated']}")

    print_section(6, total, "Collect the fresh forecast")
    job = api.wait_for_job(fresh["job_id"])
    forecast = job["result"]["forecast"]
    print(f"  Forecast {forecast['value']:.4f} [{forecast['lower']:.4f}, {forecast['upper']:.4f}]")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Job management -- list, cancel, force-new, re-trigger")
    add_common_args(parser)
    parser.add_argument("--platform-id", type=int, required=True,
                        help="Platform to forecast on")
    parser.add_argument("--config-id", type=int, required=True,
                        help="Prediction config id on that platform")
    args = parser.parse_args()
    run_demo(run_job_management, args)


if __name__ == "__main__":
    main()
