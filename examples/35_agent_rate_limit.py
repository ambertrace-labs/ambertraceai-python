"""35 — Agent Rate-Limit Gate (cumulative count, English-authored).

Proof-carrying governance for an AI agent's actions, authored in PLAIN ENGLISH.
You write the rate-limit rule in a sentence; Ambertrace compiles it to a verified
policy and PROVES every proposed action permit/deny against the CUMULATIVE count
of notifications sent so far — fail-closed, with a machine-checked proof, and the
gate is the sole executor (no effect without a prior certified permit).

The scenario: an autonomous support agent may send notifications, but the TOTAL
number sent across the session is capped. Each send writes a row to a
notifications ledger; the policy caps the running count of rows. Individually
every send is fine — the control is the CUMULATIVE total, which a per-action
check cannot express. This is the obligation the verified gate adds.

What it shows:

  1. Author the rate-limit policy in ENGLISH (cumulative-count obligation)
  2. Read back the admitted rules (plain English) + the declared input fields
  3. Open a mediated session and step a synthetic, seeded send stream:
       - sends that keep the running count within the cap -> PERMIT + proof,
         executed (the row joins the ledger)
       - the send that would push the cumulative count over the cap -> DENY +
         proof, NOT executed (the obligation fact is absent from the proof)

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The send stream is
synthetic and seeded (reproducible). The Agent Policy Gate is a preview
capability; when it is not enabled on your deployment the endpoints return 404,
which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 35_agent_rate_limit.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The rate limit. Cumulative count = number of rows in the notifications ledger.
MAX_NOTIFICATIONS = 5

# A cumulative-count policy, authored in plain English. The compiler admits a
# verified COUNT obligation: the running count of rows in the notifications
# ledger must stay at or below MAX_NOTIFICATIONS.
RATE_LIMIT_POLICY = (
    "An autonomous support agent may send notifications. Each send is recorded "
    "as a row in a notifications ledger. No more than "
    f"{MAX_NOTIFICATIONS} notifications may be sent — the running count across "
    "all rows in the notifications ledger must stay at or below "
    f"{MAX_NOTIFICATIONS}. Permit a send only when the resulting count stays "
    "within that limit."
)

# A synthetic, seeded send stream. Running count after each: 1, 2, 3, 4, 5, 6.
# The first five are within the cap; the sixth pushes the cumulative count over
# the limit of 5 — that is the one the verified gate must DENY.
#   (label, expected)
SEND_STREAM = [
    ("send 1 (running 1)", "permit"),
    ("send 2 (running 2)", "permit"),
    ("send 3 (running 3)", "permit"),
    ("send 4 (running 4)", "permit"),
    ("send 5 (running 5)", "permit"),
    ("send 6 (running 6 — OVER LIMIT)", "deny"),
]


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _print_inputs(status: dict) -> None:
    inputs = status.get("input_fields") or []
    if not inputs:
        # No declared inputs at all (e.g. a policy with no per-action operands).
        print("  No declared input fields: the gate still constrains whatever the "
              "action proposes.")
        return
    # A cumulative-count policy proves its obligation over the LEDGER of executed
    # actions; any operand columns a row contributes are surfaced as input_fields,
    # so an action supplies them as args and the gate proves the obligation over
    # the resulting ledger.
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}")


def _run_stream(api, platform_id: int, stream) -> None:
    session = api.agent_policy.create_session(
        platform_id=platform_id, goal="send notifications within the rate limit")
    sid = session["id"]
    print(f"  Mediated session {sid} opened (the gate is the sole executor).")

    for label, expected in stream:
        print(f"\n  {'-' * 66}\n  {label}")
        step = api.agent_policy.step(
            sid, tool="send_notification", args={"channel": "email"})
        verdict = (step.get("step") or {}).get("verdict") or {}
        executed = (step.get("step") or {}).get("executed")
        decision = verdict.get("decision")
        mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
        print(f"    Decision:      {str(decision).upper()}  {mark}")
        print(f"    proof_checked: {verdict.get('proof_checked')}")
        print(f"    executed:      {executed}")
        if decision != "permit" and verdict.get("denied_reason"):
            print(f"    denied_reason: {verdict.get('denied_reason')}")

    # The trace proves the mediation invariant: only the permitted sends ran.
    trace = api.agent_policy.get_session(sid).get("trace") or []
    executed = [t for t in trace if t.get("executed")]
    print(f"\n  Executed {len(executed)} of {len(trace)} proposed sends "
          "(an effect occurs only after a certified permit).")


def _author_and_run(api, policy_text: str, stream, title: str) -> bool:
    """Author a policy and run the send stream through the gate.

    Returns False (and reports cleanly) if the gate is not enabled (404)."""
    try:
        result = api.agent_policy.author(policy_text)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("\n  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) — skipping.")
            return False
        raise
    platform = result.get("platform") or {}
    print(f"  Authored verified policy -> platform {platform.get('id')} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)

    status = api.agent_policy.status()
    _print_inputs(status)

    print_section(3, 3, f"Stepping the synthetic send stream ({title})")
    _run_stream(api, platform["id"], stream)
    return True


def run_rate_limit_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the rate-limit policy (English in)")
    print(f"  POLICY:\n    {RATE_LIMIT_POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    enabled = _author_and_run(api, RATE_LIMIT_POLICY, SEND_STREAM, "cumulative count")
    if not enabled:
        return

    print("\nDone. Every decision above is proof-carrying: a permit means the "
          "kernel certified the cumulative count stays within the cap; a deny "
          "means it could NOT, fail-closed, and the send never executed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Rate-Limit Gate — AmberTrace AI verified cumulative-"
                    "count governance for AI-agent actions (English-authored)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_rate_limit_demo, args)


if __name__ == "__main__":
    main()
