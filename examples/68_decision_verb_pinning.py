"""68 -- Decision Table labels (your own words on served decisions).

A decision-table row's ``label`` is YOUR word for an outcome -- "approve" rather
than the generic "permit", "reject" rather than "deny" -- and a served decision
always carries it, on BOTH the ``authorize-action`` and ``query`` paths.  You
declare the table with ``agent_policy.author(policy_text, decision_table=...)``
(omit it and the product's binary ``{permit, deny}`` table applies).  The
machine-readable ``outcome`` (``permit`` / ``deny``, or ``None`` when nothing was
decided) and the ``permitted`` boolean are derived from each row's declared
``permits`` flag, so programmatic switching stays the same whatever words you
choose; the ``decision`` field carries the label YOU wrote.

The scenario: a loan-approval policy.

    "Applications with a credit score at or above 500 should be APPROVED.
     Applications with a credit score below 500 should be REJECTED."

declared with the table ``reject (order 2, permits False)`` /
``approve (order 1, default, permits True)``.  An ``authorize_action`` with
credit_score=700 returns ``decision="approve"``; credit_score=400 returns
``decision="reject"``.  ``outcome`` is ``"permit"`` / ``"deny"`` and ``permitted``
True / False.  The ``query`` endpoint returns the same fields, plus ``status``.

Migration note: branch on ``permitted`` to switch permit/deny, on ``decision``
for label-specific logic, and on ``status`` for abstain / indeterminate /
unavailable.  ``platforms.status(platform_id)["decision_table"]`` echoes the
table the gate was built with (``provenance``, ``applied``).

This is a verified GATE, not a dataset-trained platform -- the policy is
authored from English, so there is no domain/data upload step.  The Agent
Policy Gate is a preview capability (feature-flagged server-side); when it is
not enabled on your deployment its endpoints return 404, which this demo
reports cleanly and skips.

Creates resources on your account.  Run with --help for options.

    python 68_decision_verb_pinning.py
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_decision_table, print_section, run_demo

LOAN_POLICY = (
    "A loan-approval gate.  Applications with a credit score at or above 500 "
    "should be approved.  Applications with a credit score below 500 should be "
    "rejected."
)

# The Decision Table: your words for the two outcomes.  `permits` is what drives
# `outcome` / `permitted`; `default` is the outcome when no rule fires.
DECISION_TABLE = {
    "mode": "ladder",
    "rows": [
        {"label": "reject", "order": 2, "permits": False},
        {"label": "approve", "order": 1, "default": True, "permits": True},
    ],
}


def main(api, _args) -> None:
    # --- 1. Author the policy ------------------------------------------------
    print_section(1, 4, "Author the loan-approval policy")
    print(f"  Policy text:\n    {LOAN_POLICY}\n")
    try:
        result = api.agent_policy.author(LOAN_POLICY, decision_table=DECISION_TABLE)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) -- skipping.")
            return
        raise
    platform = result.get("platform") or {}
    pid = platform.get("id")
    admitted = result.get("admitted") or []
    print(f"  Platform {pid} ({platform.get('status')}, "
          f"verified={platform.get('verified_profile')})")
    print(f"  Admitted {len(admitted)} rule(s):")
    for rule in admitted:
        print(f"    - {rule.get('name')}: "
              f"{(rule.get('description') or '').strip()}")

    # --- 2. Inspect the decision table ---------------------------------------
    print_section(2, 4, "Decision table the gate was built with")
    status = api.platforms.status(pid)
    print_decision_table(status.get("decision_table"))
    for warning in status.get("decision_table_warnings") or []:
        print(f"  [warning] {warning.get('check', '?')}: {warning.get('message')}")

    # --- 3. Authorize two actions: one approved, one rejected -----------------
    print_section(3, 4, "Authorize actions (your labels on served decisions)")

    cases = [
        ("Good credit (700)", {"credit_score": 700}, "approve", "permit", True),
        ("Bad credit (400)",  {"credit_score": 400}, "reject",  "deny",   False),
    ]
    for label, args, expected_decision, expected_outcome, expected_permitted in cases:
        print(f"\n  {label}:")
        verdict = api.agent_policy.authorize_action(
            pid, tool="apply_loan", args=args)
        decision = verdict.get("decision")
        outcome = verdict.get("outcome")
        permitted = verdict.get("permitted")
        proof = verdict.get("proof_checked")
        mark = "[OK]" if decision == expected_decision else f"[!! expected {expected_decision}]"
        print(f"    decision:      {decision}  {mark}")
        mark = "[OK]" if outcome == expected_outcome else f"[!! expected {expected_outcome}]"
        print(f"    outcome:       {outcome}  {mark}  (derived from the row's `permits`)")
        mark = "[OK]" if permitted == expected_permitted else f"[!! expected {expected_permitted}]"
        print(f"    permitted:     {permitted}  {mark}")
        print(f"    status:        {verdict.get('status')}")
        print(f"    proof_checked: {proof}")
        if verdict.get("denied_reason"):
            print(f"    denied_reason: {verdict.get('denied_reason')}")

    # --- 4. Query path: same fields -------------------------------------------
    print_section(4, 4, "Query path (decision / outcome / permitted / status)")

    query_cases = [
        ("Permit (score 700)", {"credit_score": 700}, "approve", "permit", True),
        ("Deny (score 400)",   {"credit_score": 400}, "reject",  "deny",   False),
    ]
    for label, facts, expected_decision, expected_outcome, expected_permitted in query_cases:
        print(f"\n  {label}:")
        qr = api.platforms.query(pid, query="check credit", facts=facts)
        decision = qr.get("decision")
        outcome = qr.get("outcome")
        permitted = qr.get("permitted")
        mark = "[OK]" if decision == expected_decision else f"[!! expected {expected_decision}]"
        print(f"    decision:      {decision}  {mark}")
        mark = "[OK]" if outcome == expected_outcome else f"[!! expected {expected_outcome}]"
        print(f"    outcome:       {outcome}  {mark}")
        mark = "[OK]" if permitted == expected_permitted else f"[!! expected {expected_permitted}]"
        print(f"    permitted:     {permitted}  {mark}  (boolean, for execute-or-block logic)")
        print(f"    status:        {qr.get('status')}")
        # Programmatic switching -- use permitted, not the label:
        if permitted:
            print("    -> action is WITHIN policy (programmatic: switch on 'permitted')")
        else:
            print("    -> action is OUTSIDE policy (programmatic: switch on 'permitted')")

    print("\n  The 'decision' field carries your decision-table label;")
    print("  'outcome' and 'permitted' follow each row's declared `permits`;")
    print("  'status' says whether a verdict was reached (decided | indeterminate | ...).")
    print("  Use permitted (not decision) for execute-or-block logic.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_common_args(parser)
    run_demo(main, parser.parse_args())
