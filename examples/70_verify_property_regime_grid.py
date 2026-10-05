"""70 -- Certified search: is every cell of my regime grid covered by EXACTLY ONE verdict?

``platforms.verify_property(property="exactly_one_verdict")`` certifies, for a platform
whose decision rules classify a *regime grid* you declare (e.g. priced move x incentive
sign x reaction function), that **every cell derives exactly one verdict** from the
platform's own active decision rules -- no uncovered cell, no double-covered cell.  It
returns exactly one of

* ``HOLDS``    -- every cell of the grid was checked by a machine-checked enumeration
                  (``certified == "exhaustive"``; ``search.space_size`` is the product of
                  your declared domain sizes);
* ``VIOLATED`` -- the first violating cell (``witness``; ``witness_detail`` says which
                  ``verdicts`` derive there -- ``[]`` = uncovered, 2+ = double-covered);
* ``ABSTAIN``  -- no verdict, with a ``reason``: ``bound`` below the grid size, a rule
                  condition that is not a scalar test on a declared grid field
                  (``condition_out_of_fragment``), a rule field you left out of the grid
                  (``field_outside_grid``), or no active verdict rules.  NEVER a pass.

This example is read-only: it certifies the rules of an EXISTING platform (pass
``--platform-id``; default: your first platform) against the grid you give it.  Edit
``GRID`` to the fields and domains your platform's rules actually use -- the default
grid below matches the ``priced`` / ``incentive`` / ``reaction`` regime classifier shape
and will ABSTAIN (``field_outside_grid`` or ``no_active_verdict_rules``) on a platform
with different rules, which is the intended, honest answer.

Each call is an async server-side job: the SDK starts it (202) and polls
``GET /api/v1/jobs/{id}`` every 5s, so ``verify_property`` reads as one blocking call.

    python 70_verify_property_regime_grid.py --platform-id 123
"""

from __future__ import annotations

import argparse
import sys

from _common import add_common_args, make_client, print_section

GRID = [
    {"field": "priced", "domain": ["neg", "zero", "pos"]},
    {"field": "incentive", "domain": ["neg", "zero", "pos"]},
    {"field": "reaction", "domain": ["hawk", "dove"]},
]
GRID_SIZE = 3 * 3 * 2


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_common_args(parser)
    parser.add_argument("--platform-id", type=int, default=None,
                        help="Platform whose decision rules are certified "
                             "(default: your first platform).")
    args = parser.parse_args()
    api = make_client(args)
    try:
        pid = args.platform_id
        if pid is None:
            platforms = api.platforms.list()
            if not platforms:
                print("No platform in this account -- create one first (see examples 00/10), "
                      "then re-run; exactly_one_verdict certifies a platform's own rules.")
                return
            pid = platforms[0]["id"]
        print(f"Using platform {pid}")

        print_section(1, 2, "Totality + exclusivity over the declared regime grid")
        res = api.platforms.verify_property(
            pid, property="exactly_one_verdict",
            space={"variables": GRID, "bound": GRID_SIZE})
        print(f"    result:        {res.result}")
        print(f"    certified:     {res.certified}")
        print(f"    proof_checked: {res.proof_checked}")
        print(f"    search:        {dict(res.search)}")
        print(f"    answer:        {res.answer}")
        assert res.proof_summary.startswith(res.result + ":"), res.proof_summary
        assert res.answer.startswith(res.result), res.answer
        if res.result == "HOLDS":
            assert res.certified == "exhaustive" and res.search["space_size"] == GRID_SIZE
            print("    every cell derives exactly one verdict.")
        elif res.result == "VIOLATED":
            detail = res.witness_detail
            print(f"    violating cell: {dict(res.witness)} (#{res.witness_index})")
            print(f"    verdicts there: {detail['verdicts']}  ({detail['coverage']})")
            assert res.certified == "witness" and res.witness_detail["coverage"] in (
                "uncovered", "double_covered")
        else:
            assert res.proof_checked is False and res.certified is None
            print(f"    no verdict: {res.reason} -- this is NOT a pass.")

        print_section(2, 2, "A bound below the grid size is an explicit ABSTAIN")
        res = api.platforms.verify_property(
            pid, property="exactly_one_verdict",
            space={"variables": GRID, "bound": GRID_SIZE - 1})
        print(f"    result: {res.result}  reason: {res.get('reason')}")
        assert res.result == "ABSTAIN" and res.proof_checked is False

        print("\nDone.")
    finally:
        api.close()


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:  # a verdict that disagrees with itself is a defect
        print(f"\nFAILED: {exc}", file=sys.stderr)
        sys.exit(1)
