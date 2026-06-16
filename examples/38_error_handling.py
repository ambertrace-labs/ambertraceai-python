"""38 — Error Handling & job types.

A tour of the SDK's error surface and the two kinds of jobs you poll. Every
deliberate failure here is caught, so the script always exits 0. Read-only —
creates nothing on your account.

  1. Catch AmbertraceError on a bad domain lookup (status_code / code / str)
  2. Catch AmbertraceError on a bad platform lookup (same shape)
  3. The verified fail-closed pattern (HTTP 503 / "service_unavailable")
  4. The two job types from wait_for_job (ontology vs build)

Run with --help for options.

    python 38_error_handling.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# An id that will not exist on any account — used to provoke a 404.
BOGUS_ID = 999999999


def run_error_handling_demo(api, args: argparse.Namespace) -> None:
    total = 4

    # ------------------------------------------------------------------
    # (a) AmbertraceError on a bad domain lookup
    # ------------------------------------------------------------------
    print_section(1, total, "AmbertraceError on a bad domain lookup")
    print(f"  Calling api.domains.get({BOGUS_ID}) — this domain does not exist.")
    try:
        api.domains.get(BOGUS_ID)
    except AmbertraceError as exc:
        print(f"  Caught AmbertraceError:")
        print(f"    exc.status_code = {exc.status_code!r}   # HTTP status, e.g. 404")
        print(f"    exc.code        = {exc.code!r}   # machine-readable, e.g. 'not_found'")
        print(f"    str(exc)        = {str(exc)!r}   # human-readable message")
    else:
        print("  (no error raised — unexpected for a bogus id)")
    print(
        "  Every API failure raises AmbertraceError; .status_code is the HTTP\n"
        "  code, .code a stable string you can branch on, and str(exc) the\n"
        "  server's message. Catch it once around your call site."
    )

    # ------------------------------------------------------------------
    # (b) AmbertraceError on a bad platform lookup — same pattern
    # ------------------------------------------------------------------
    print_section(2, total, "AmbertraceError on a bad platform lookup")
    print(f"  Calling api.platforms.get({BOGUS_ID}) — same try/except shape.")
    try:
        api.platforms.get(BOGUS_ID)
    except AmbertraceError as exc:
        print(f"    exc.status_code = {exc.status_code!r}")
        print(f"    exc.code        = {exc.code!r}")
        print(f"    str(exc)        = {str(exc)!r}")
    else:
        print("  (no error raised — unexpected for a bogus id)")

    # ------------------------------------------------------------------
    # (c) The verified fail-closed pattern (HTTP 503 / service_unavailable)
    # ------------------------------------------------------------------
    print_section(3, total, "Verified fail-closed pattern (HTTP 503)")
    print(
        "  On a VERIFIED platform, a query the reasoning engine cannot certify\n"
        "  is refused fail-closed: the SDK raises AmbertraceError with\n"
        "    status_code == 503  and  code == 'service_unavailable'.\n"
        "  No (possibly wrong) answer is ever returned. Catch and branch on it:\n"
    )
    print(
        "      try:\n"
        "          report = api.platforms.query(platform_id, query=query)\n"
        "      except AmbertraceError as exc:\n"
        "          fail_closed = (\n"
        "              getattr(exc, 'status_code', None) == 503\n"
        "              or getattr(exc, 'code', '') == 'service_unavailable'\n"
        "          )\n"
        "          if fail_closed:\n"
        "              ...  # surface 'could not certify' — do NOT treat as an answer\n"
        "          else:\n"
        "              raise\n"
    )
    print(
        "  This is exactly the shape _common.query_and_report uses. We cannot\n"
        "  force a real 503 here, so the catch is demonstrated defensively: any\n"
        "  AmbertraceError below is classified the same way query_and_report does."
    )
    try:
        # Defensive demonstration: this bogus query will error; we classify the
        # exception with the identical fail-closed test used in production code.
        api.platforms.query(BOGUS_ID, query="Should this be permitted?")
    except AmbertraceError as exc:
        fail_closed = (
            getattr(exc, "status_code", None) == 503
            or getattr(exc, "code", "") == "service_unavailable"
        )
        verdict = "fail-closed (could not certify)" if fail_closed else "ordinary error"
        print(f"  Caught AmbertraceError → classified as: {verdict}")
        print(f"    (status_code={exc.status_code!r}, code={exc.code!r})")
    else:
        print("  (no error raised)")

    # ------------------------------------------------------------------
    # (d) The two job types from wait_for_job
    # ------------------------------------------------------------------
    print_section(4, total, "The two job types from wait_for_job")
    print(
        "  api.wait_for_job(job_id) returns one of two job TYPES — poll the\n"
        "  right id for the result you want:\n"
    )
    print(
        "    • ONTOLOGY job  (type='ontology', from domains.build_ontology)\n"
        "        job['result'] is the ontology itself. It does NOT carry\n"
        "        generation_diagnostics.\n"
    )
    print(
        "    • BUILD job     (type='build', the build_job from platforms.create)\n"
        "        job['result']['build_quality']            → build-quality summary\n"
        "        job['result']['generation_diagnostics']   → decision-coverage detail\n"
    )
    print(
        "  A consumer polling the ontology job will never see\n"
        "  generation_diagnostics — poll the platform BUILD job id instead.\n"
        "  See example 39 for the end-to-end build-diagnostics walkthrough."
    )

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Error Handling & job types — AmberTrace AI SDK mechanics demo",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_error_handling_demo, args)


if __name__ == "__main__":
    main()
