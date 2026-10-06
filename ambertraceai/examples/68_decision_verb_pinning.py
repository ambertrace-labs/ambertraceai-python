"""68 -- Decision Verb Pinning (policy-authored verbs on served decisions).

When you author a policy in plain English with domain-specific verbs --
"approve" rather than the canonical "permit", or "reject" rather than "deny" --
the platform preserves YOUR words on every served decision, on BOTH the
``authorize-action`` and ``query`` paths.  The machine-readable ``outcome``
field (``permit`` / ``deny`` / ``indeterminate``) and ``permitted`` boolean
stay canonical for programmatic switching; the ``decision`` field carries the
verb YOU wrote.

The scenario: a loan-approval policy.

    "Applications with a credit score at or above 500 should be APPROVED.
     Applications with a credit score below 500 should be REJECTED."

After authoring, an ``authorize_action`` with credit_score=700 returns
``decision="approve"`` (not the generic "permit").  An action with
credit_score=400 returns ``decision="reject"`` (not "deny").  The ``outcome``
field is unchanged ("permit" / "deny") so downstream automations that switch
on ``outcome`` keep working.  The ``query`` endpoint returns the same
three-field contract: ``decision`` (author verb), ``outcome`` (canonical),
``permitted`` (boolean).

``platforms.status(platform_id)["decision_vocabulary"]`` (when declared) lists
every verb the policy uses (``None`` otherwise); when verbs are from the built-in families (approve,
reject, etc.) no explicit vocabulary is needed -- the gate infers the mapping.

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

from _common import add_common_args, print_section, run_demo

LOAN_POLICY = (
    "A loan-approval gate.  Applications with a credit score at or above 500 "
    "should be approved.  Applications with a credit score below 500 should be "
    "rejected."
)


def main(api, _args) -> None:
    # --- 1. Author the policy ------------------------------------------------
    print_section(1, 4, "Author the loan-approval policy")
    print(f"  Policy text:\n    {LOAN_POLICY}\n")
    try:
        result = api.agent_policy.author(LOAN_POLICY)
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

    # --- 2. Inspect the vocabulary -------------------------------------------
    print_section(2, 4, "Decision vocabulary / verb map")
    status = api.platforms.status(pid)
    vocab = status.get("decision_vocabulary")
    if vocab:
        print("  Declared decision_vocabulary:")
        for v in vocab.get("verbs") or []:
            print(f"    {v.get('verb')}: restrictive={v.get('restrictive')}, "
                  f"default={v.get('default', False)}")
    else:
        print("  No explicit decision_vocabulary declared -- the gate infers the")
        print("  verb mapping from built-in families (approve -> permit-family, "
              "reject -> deny-family).")

    # --- 3. Authorize two actions: one approved, one rejected -----------------
    print_section(3, 4, "Authorize actions (decision verb pinning)")

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
        print(f"    outcome:       {outcome}  (machine-readable, always canonical)")
        print(f"    permitted:     {permitted}")
        print(f"    proof_checked: {proof}")
        if verdict.get("denied_reason"):
            print(f"    denied_reason: {verdict.get('denied_reason')}")

    # --- 4. Query path: same three-field contract ----------------------------
    print_section(4, 4, "Query path (outcome / permitted on queries)")

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
        print(f"    outcome:       {outcome}  (canonical, always permit/deny/indeterminate)")
        print(f"    permitted:     {permitted}  (boolean, for execute-or-block logic)")
        # Programmatic switching -- use outcome/permitted, not decision:
        if permitted:
            print("    -> action is WITHIN policy (programmatic: switch on 'permitted')")
        else:
            print("    -> action is OUTSIDE policy (programmatic: switch on 'permitted')")

    print("\n  The 'decision' field carries the policy author's verb;")
    print("  'outcome' and 'permitted' stay canonical for programmatic use.")
    print("  Use outcome/permitted (not decision) for execute-or-block logic.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    add_common_args(parser)
    run_demo(parser, main)
