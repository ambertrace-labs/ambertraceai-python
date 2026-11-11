"""77 -- Certified search over YOUR OWN game: Nash equilibrium, dominance, Pareto.

``platforms.verify_property`` accepts a custom finite *normal-form game* in
``space["game"]`` -- 2 to 6 players (up to 30 when the game is symmetric: identical action
sets and a symmetric table), each with a finite action set, and an explicit payoff
table (one row per action profile) -- and certifies game-theoretic claims over it by
exhaustive, machine-checked enumeration:

* ``nash_equilibrium``   -- ``space["profile"]``: no player can profit by deviating alone;
* ``dominant_strategy``  -- ``space["player"]`` + ``space["action"]`` (``strict=True`` for
                            strict dominance): the action does at least as well as every
                            alternative against EVERY opponent profile;
* ``best_response``      -- ``space["player"]`` + ``space["action"]`` +
                            ``space["opponent_profile"]``;
* ``pareto_optimal``    -- ``space["profile"]``: HOLDS when no profile Pareto-dominates it;
                            VIOLATED returns the dominating profile;
* ``pareto_dominated``  -- the dual: HOLDS when a dominating profile EXISTS (it is the
                            ``witness``); VIOLATED (exhaustive) when none does.

Each returns the same tri-state verdict as the mechanism library: ``HOLDS``
(``certified == "exhaustive"``), ``VIOLATED`` (a ``witness`` re-certified through the
trusted kernel; ``witness_recertification`` carries EVERY player's payoff at the claimed
and the deviating / dominating profile) or ``ABSTAIN`` (``reason``: ``over_bound``,
``over_ceiling``, ``game_too_large``, ``payoff_table_incomplete`` ... -- never a pass).
A payoff cell may be an integer or ``{"param": name, "mul": 1, "add": 0}`` resolved from
``game["parameters"]`` (integers you supply, e.g. copied from a certified platform
output); the resolved table is echoed back as ``resolved_payoffs``.

The game below (P1 = U/M/D, P2 = L/R; payoffs P1, P2) has the single pure equilibrium
(U, L), which the profile (M, R) Pareto-dominates:

            L        R
      U   (2,1)    (0,0)
      M   (1,2)    (3,1)
      D   (0,0)    (1,3)

Creates nothing but short-lived job records (it only reads your platforms).

    python 77_verify_property_custom_game.py
"""

from __future__ import annotations

import argparse
import sys

from _common import add_common_args, make_client, print_section

GAME = {
    "players": [["U", "M", "D"], ["L", "R"]],
    "payoffs": [
        {"actions": ["U", "L"], "utilities": [2, 1]},
        {"actions": ["U", "R"], "utilities": [0, 0]},
        {"actions": ["M", "L"], "utilities": [1, 2]},
        {"actions": ["M", "R"], "utilities": [3, 1]},
        {"actions": ["D", "L"], "utilities": [0, 0]},
        {"actions": ["D", "R"], "utilities": [1, 3]},
    ],
}


def _show(res) -> None:
    print(f"    result:        {res.result}")
    print(f"    certified:     {res.certified}")
    print(f"    proof_checked: {res.proof_checked}")
    print(f"    search:        {dict(res.search)}")
    if res.witness:
        print(f"    witness:       {dict(res.witness)}")
    if res.get("witness_recertification"):
        print(f"    recertified:   {dict(res.witness_recertification)}")
    if res.get("reason"):
        print(f"    reason:        {res.reason}")
    print(f"    summary:       {res.proof_summary}")
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

        def verify(prop, **claim):
            return api.platforms.verify_property(
                pid, property=prop, space={"game": GAME, "bound": 1000, **claim})

        print_section(1, 5, "(U, L) is the Nash equilibrium -> HOLDS, exhaustive")
        res = verify("nash_equilibrium", profile=["U", "L"])
        _show(res)
        assert res.result == "HOLDS" and res.certified == "exhaustive"
        assert res.search["space_size"] == 10  # 2 players x 5 distinct actions in the game

        print_section(2, 5, "(M, R) is not -> VIOLATED + the profitable deviation")
        res = verify("nash_equilibrium", profile=["M", "R"])
        _show(res)
        assert res.result == "VIOLATED" and res.certified == "witness"
        assert (res.witness["agent"], res.witness["misreport"]) == (2, "L")
        rec = res.witness_recertification
        assert (rec["truthful_payoffs"], rec["deviated_payoffs"]) == ([3, 1], [1, 2])

        print_section(3, 5, "the equilibrium (U, L) is Pareto-dominated by (M, R)")
        res = verify("pareto_optimal", profile=["U", "L"])
        _show(res)
        assert res.result == "VIOLATED"
        assert dict(res.witness) == {"act_1": "M", "act_2": "R"}  # (3,1) vs (2,1)

        print_section(4, 5, "dominance: P1's U fails against R; P2's R is a best reply to D")
        res = verify("dominant_strategy", player=1, action="U")
        _show(res)
        assert res.result == "VIOLATED" and res.witness["act_2"] == "R"
        res = verify("best_response", player=2, action="R", opponent_profile=["D"])
        _show(res)
        assert res.result == "HOLDS"

        print_section(5, 5, "a bound below the space is an explicit ABSTAIN")
        res = api.platforms.verify_property(
            pid, property="nash_equilibrium",
            space={"game": GAME, "bound": 9, "profile": ["U", "L"]})
        _show(res)
        assert res.result == "ABSTAIN" and res.reason == "over_bound"
        assert res.proof_checked is False and res.certified is None

        print("\nDone.")
    finally:
        api.close()


if __name__ == "__main__":
    try:
        main()
    except AssertionError as exc:  # a verdict that disagrees with itself is a defect
        print(f"\nFAILED: {exc}", file=sys.stderr)
        sys.exit(1)
