"""69 -- Certified search: prove a mechanism strategy-proof (or find the manipulation).

``platforms.query`` certifies ONE input.  ``platforms.verify_property`` certifies a
MECHANISM UNIVERSALLY: "for EVERY profile of preferences and EVERY deviation, no
agent profits from misreporting."  It returns exactly one of

* ``HOLDS``    -- every member of the finite space was checked by a machine-checked
                  enumeration (``certified == "exhaustive"``, ``search.complete`` is
                  True, ``search.space_size`` is the product of your declared domain
                  sizes);
* ``VIOLATED`` -- a certified counterexample (``witness``): a concrete profile + agent
                  + misreport that profits, independently re-certified
                  (``certified == "witness"``);
* ``ABSTAIN``  -- no verdict, with a ``reason``: your ``bound`` is smaller than the
                  space, or the space is above the platform ceiling.  ABSTAIN is
                  NEVER a pass.

Three cases, run against one platform (any platform in your account scopes the call;
the mechanism is declared in ``space``):

  (a) 3-candidate plurality, 3 voters  -> VIOLATED + the manipulation
      (Gibbard-Satterthwaite: no onto, non-dictatorial rule over 3+ alternatives is
      strategy-proof)
  (b) 2-candidate majority, and a discrete Vickrey auction  -> HOLDS, exhaustive
  (c) the same plurality with a bound BELOW the space, and a 4-candidate space above
      the platform ceiling  -> ABSTAIN

``result``, ``certified``, ``proof_checked``, ``proof_summary`` and the SDK-rendered
``answer`` always name the SAME verdict -- the script asserts it.

Creates nothing: it only reads your platforms.  Run with --help for options.

    python 69_verify_property_strategy_proof.py
"""

from __future__ import annotations

import argparse
import math
import sys

from _common import add_common_args, make_client, print_section


def _show(res) -> None:
    print(f"    result:        {res.result}")
    print(f"    certified:     {res.certified}")
    print(f"    proof_checked: {res.proof_checked}")
    print(f"    search:        {dict(res.search)}")
    if res.witness:
        print(f"    witness:       {dict(res.witness)}")
    if res.get("reason"):
        print(f"    reason:        {res.reason}")
    print(f"    answer:        {res.answer}")
    # One verdict everywhere: result, summary and the SDK answer agree.
    assert res.proof_summary.startswith(res.result + ":"), res.proof_summary
    assert res.answer.startswith(res.result), res.answer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_common_args(parser)
    parser.add_argument("--platform-id", type=int, default=None,
                        help="Platform to scope the calls to (default: your first platform).")
    args = parser.parse_args()
    api = make_client(args)
    try:
        pid = args.platform_id
        if pid is None:
            platforms = api.platforms.list()
            if not platforms:
                print("No platform in this account -- create one first (see examples 00/10), "
                      "then re-run; verify_property is scoped to a platform.")
                return
            pid = platforms[0]["id"]
        print(f"Using platform {pid}")

        print_section(1, 3, "(a) 3-candidate plurality is manipulable -> VIOLATED + witness")
        plurality = {"mechanism": "plurality", "agents": 3,
                     "domain": ["A", "B", "C"], "bound": 2000}
        res = api.platforms.verify_property(pid, property="strategy_proof", space=plurality)
        _show(res)
        assert res.result == "VIOLATED" and res.certified == "witness"
        print("    the manipulation: agent", res.witness["agent"], "reports",
              res.witness["misreport"], "instead of their true top choice.")

        print_section(2, 3, "(b) majority-of-2 and Vickrey are strategy-proof -> HOLDS")
        majority = {"mechanism": "majority", "agents": 4, "domain": ["A", "B"], "bound": 128}
        res = api.platforms.verify_property(pid, property="strategy_proof", space=majority)
        _show(res)
        assert res.result == "HOLDS" and res.certified == "exhaustive"
        assert res.search["space_size"] == 2 ** 4 * 4 * 2  # 16 type profiles x 4 agents x 2 reports
        assert res.search["complete"] is True

        vickrey = {"mechanism": "vickrey", "agents": 2, "domain": [0, 1, 2, 3], "bound": 128}
        res = api.platforms.verify_property(pid, property="strategy_proof", space=vickrey)
        _show(res)
        assert res.result == "HOLDS" and res.search["space_size"] == 4 * 4 * 2 * 4

        print_section(3, 3, "(c) beyond the bound / ceiling -> ABSTAIN (never a silent pass)")
        res = api.platforms.verify_property(
            pid, property="strategy_proof", space={**plurality, "bound": 1943})
        _show(res)
        assert res.result == "ABSTAIN" and res.reason == "over_bound"
        assert res.proof_checked is False and res.certified is None

        four = {"mechanism": "plurality", "agents": 3, "domain": ["A", "B", "C", "D"],
                "bound": 10 ** 9}
        res = api.platforms.verify_property(pid, property="strategy_proof", space=four)
        _show(res)
        assert res.result == "ABSTAIN" and res.reason == "over_ceiling"
        assert res.search["space_size"] == math.factorial(4) ** 3 * 3 * 4  # 165888

        print("\nDone.")
    finally:
        api.close()


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:  # a verdict that disagrees with itself is a defect
        print(f"\nFAILED: {exc}", file=sys.stderr)
        sys.exit(1)
