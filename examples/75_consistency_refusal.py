"""75 -- consistency refusal: a build that contradicts your own description (C9).

Before a verified platform is served, the platform checks the description's
residual ("otherwise") claim against the decisions the built table actually
serves over YOUR ingested rows. If they contradict -- the description says
"approved otherwise" but the table's default row is ``deny``, so the rows no other
rule decides are served ``deny`` -- the build is REFUSED, because the platform
would otherwise serve the opposite of what you wrote.

Two outcomes to handle:

  * REFUSED build -- ``build_platform`` raises ``RuntimeError`` whose message reads
    ``consistency: Your description says "<sentence>" (otherwise -> '<label>'), but
    the built decision table serves a different decision on N of M rows that no
    other rule decides (e.g. credit_score=600 -> served 'deny', ...). Fix the
    description or the table's default row.`` It carries the description sentence
    and witness rows. Fix the description or the default row, then rebuild.
  * ADVISORY -- when the server's ``AMBERTRACE_CONSISTENCY_BLOCK`` flag is off (or
    the finding is advisory-only) the build completes and the same finding is
    recorded as a ``C9`` / ``claim_contradicted`` entry in
    ``platforms.status(id)["decision_table_warnings"]``, with ``sentence``, ``row``
    and ``witnesses`` (``[{"row": {...}, "served": "<label>"}]``).

The refusal is live only on a deployment where ``AMBERTRACE_CONSISTENCY_BLOCK`` is
on; elsewhere you get the C9 advisory instead. Handle both.

Creates resources on your account. Run with --help for options.

    python 75_consistency_refusal.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    create_domain,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

INVERTED_DESCRIPTION = (
    "Lending screening for personal loans. An application is denied when the "
    "credit_score is below 600; it is approved otherwise."
)
# The table's DEFAULT row is deny -- the opposite of "approved otherwise".
INVERTED_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "approve", "order": 1, "permits": True, "values": ["approved"]},
        {"label": "deny", "order": 2, "default": True, "permits": False,
         "values": ["denied"]},
    ],
}
# Fix: the default row now matches the description's "approved otherwise".
FIXED_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "deny", "order": 2, "permits": False, "values": ["denied"]},
        {"label": "approve", "order": 1, "default": True, "permits": True,
         "values": ["approved"]},
    ],
}


def consistency_advisories(status: dict[str, Any]) -> list[dict[str, Any]]:
    """The C9 ``claim_contradicted`` findings on a platform status."""
    return [w for w in status.get("decision_table_warnings") or []
            if w.get("check") == "C9"]


def _build(api, args, table, label):
    domain = create_domain(
        api, name=f"Consistency demo ({label})", description=INVERTED_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    api.domains.set_decision_table(domain["id"], table)
    domain = build_ontology(api, domain["id"])
    return build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau)


def run_refusal(api, args: argparse.Namespace) -> None:
    print_section(1, 2, "Building with an inverted default row (deny, description says approve)")
    try:
        platform = _build(api, args, INVERTED_TABLE, "inverted")
    except RuntimeError as exc:
        # Refused: the message carries the description sentence + witness rows.
        print(f"  Build REFUSED:\n    {exc}")
    else:
        print(f"  Build completed (platform {platform['id']}); the refusal is off on this "
              "deployment, so look for the C9 advisory:")
        for warning in consistency_advisories(api.platforms.status(platform["id"])):
            print(f"    [C9] {warning.get('message')}")
            for witness in warning.get("witnesses") or []:
                print(f"      witness {witness.get('row')} -> served {witness.get('served')!r}")

    print_section(2, 2, "Rebuilding with the default row matching the description")
    platform = _build(api, args, FIXED_TABLE, "fixed")
    status = api.platforms.status(platform["id"])
    print(f"  Platform {platform['id']} ({status.get('status')}); "
          f"C9 advisories: {len(consistency_advisories(status))}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Consistency refusal -- a build whose table contradicts the description")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="CSV file to upload (default: loan_applications.csv)")
    args = parser.parse_args()
    run_demo(run_refusal, args)


if __name__ == "__main__":
    main()
