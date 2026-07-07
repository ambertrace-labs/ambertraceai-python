"""28 — Agent Policy Gate: CI/CD deployment gate (per-action, proof-carrying).

Proof-carrying governance for a software-supply-chain / CI-CD deploy agent,
authored in PLAIN ENGLISH. An untrusted deployment agent proposes deploy/rollback
actions; Ambertrace compiles the English policy to a verified policy and PROVES
every proposed action permit/deny against it — fail-closed, with a machine-checked
proof. The LLM only *proposes*; the kernel *proves*.

Companion to 27 (single-action clinical-triage) and 25 (cumulative spend-budget),
which use clinical / financial policies. This one is the software-supply-chain
case: every rule is a PER-ACTION condition — an enum allowlist (tool,
target_environment), a boolean precondition (ci_passed, security_scan_passed,
code_review_approved, change_ticket_approved, within_change_window), a scalar
comparison (rollout_pct at most 10), or a cross-field inequality (the approver must
not be the author) — the obligation class that compiles cleanly today.

SEPARATION OF DUTIES (cross-field inequality — now composes)
------------------------------------------------------------
A classic deploy control is *separation of duties*: "the approver must not be the
author" — a cross-field inequality between two action fields. The production permit
now carries it (``approver`` != ``author``), and it composes correctly with the
other per-action conditions: an all-green production deploy with approver != author
PERMITS, and the same action with approver == author DENIES. (When this example was
first published the cross-field inequality did not yet compose with the conditional
permits — the compiler reverted to a satisfaction-field conflation and within-policy
prod deploys wrongly denied; that enforcement bug is fixed.) The gate proves the
inequality directly — there is no ``*_check_passed`` discharge fact to supply, and the
policy now compiles finding-free.

TEMPORAL / SEQUENCING — a NATIVE gate primitive (see example 40)
----------------------------------------------------------------
Two classic supply-chain rules are inherently *temporal / sequencing*:

  - "review must happen BEFORE merge / deploy"        (an ordering obligation)
  - "no more than N deploys within a window"          (a rate obligation)

These are now a NATIVE part of the verified fragment — an ordering/precedence leaf,
a bounded-window rate leaf, and a request/response pairing leaf that fold over the
session's ORDERED ledger of prior executed actions. So a policy like *"permit a
deploy for a service only when it is preceded by an approval for the same service
in the same session"* authors a real happens-before obligation the kernel proves
over the accumulated order — see ``40_agent_policy_gate_temporal.py`` for a runnable
review-before-deploy gate. Temporal obligations need a ``create_session`` + ``step``
loop (the ledger records only executed actions, in order); a single
``authorize_action`` gates an empty ledger.

THIS example stays PER-ACTION on purpose (single-shot ``authorize_action``, no
session), so it expresses the two time-flavoured requirements as CALLER-SUPPLIED
boolean preconditions instead — a valid, simpler pattern when you already hold the
booleans and don't need the gate to reason about order itself:

  - ``within_change_window`` — the mediating harness computes "is now inside the
    approved window?" and supplies the boolean; the gate proves the deploy is
    permitted only when it is true.
  - ``code_review_approved`` — set true only once review has completed; the gate
    proves "not merged without an approved review".

Trade-off: the boolean-precondition pattern trusts the harness to compute those
booleans truthfully; the native precedence obligation (example 40) proves the
ordering from the ledger itself. Use precondition booleans for a one-shot gate; the
temporal leaf + a session when you want the ORDER proven.

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. Authoring REPLACES the org's
single agent-policy gate (see 25/27). The Agent Policy Gate is a preview capability
(feature-flagged server-side); when it is not enabled — or your credentials lack
write authority over an existing org gate — ``author`` returns 404, which this demo
reports cleanly and skips.

Run with --help for options.

    python 28_agent_policy_gate_cicd.py
    python 28_agent_policy_gate_cicd.py -v
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The CI/CD deployment policy, authored in plain English. Every clause is a
# per-action condition (enum allowlist / boolean precondition / scalar comparison).
POLICY = (
    "A deployment agent proposes CI/CD actions. Each action has a tool, a "
    "target_environment, an integer rollout_pct, an author, an approver, and the "
    "boolean flags ci_passed, security_scan_passed, code_review_approved, "
    "change_ticket_approved, and within_change_window. Only allow actions whose tool "
    "is deploy or rollback. "
    "Deny any action whose target_environment is not dev, staging, or production. "
    "Permit a deploy only when ci_passed is true, security_scan_passed is true, "
    "code_review_approved is true, change_ticket_approved is true, "
    "within_change_window is true, rollout_pct is at most 10, and the approver is "
    "not the author. "
    "Permit a rollback to dev, staging, or production."
)

# A fully-compliant production deploy; each deny case below flips exactly one fact.
GOOD = {
    "tool": "deploy", "target_environment": "production", "rollout_pct": 10,
    "author": "alice", "approver": "bob",
    "ci_passed": True, "security_scan_passed": True, "code_review_approved": True,
    "change_ticket_approved": True, "within_change_window": True,
}


def _case(label: str, expected: str, **overrides) -> tuple[str, dict, str]:
    args = dict(GOOD)
    args.update(overrides)
    return label, args, expected


# (label, args, expected_decision) — the temporal preconditions are the
# interesting ones (within_change_window / code_review_approved).
SUITE = [
    _case("compliant production deploy (all green, rollout=10 boundary)", "permit"),
    _case("CI not passed", "deny", ci_passed=False),
    _case("security scan failed", "deny", security_scan_passed=False),
    _case("NO approved review (review-before-merge precondition)", "deny",
          code_review_approved=False),
    _case("OUTSIDE the change window (temporal precondition)", "deny",
          within_change_window=False),
    _case("no change ticket", "deny", change_ticket_approved=False),
    _case("rollout 50% (> 10 canary cap)", "deny", rollout_pct=50),
    # Separation of duties — the approver must not be the author (a cross-field
    # inequality between two action fields). This now composes with the per-env
    # conditional permits (enforced as of deploy 2c4caa20962b); see the docstring.
    _case("SoD VIOLATION: approver == author", "deny", author="alice", approver="alice"),
    _case("SoD satisfied: approver != author (all else green)", "permit",
          author="alice", approver="carol"),
    _case("unknown target env 'qa' (env allowlist)", "deny", target_environment="qa"),
    _case("forbidden tool terraform_destroy (action-type allowlist)", "deny",
          tool="terraform_destroy"),
    # rollback is the safety valve — permitted to a known env even with red flags
    # (it does NOT have to satisfy the deploy preconditions):
    _case("rollback to production (safety valve, deploy flags irrelevant)", "permit",
          tool="rollback", ci_passed=False, code_review_approved=False,
          within_change_window=False),
    _case("rollback to unknown env 'qa' (env allowlist still applies)", "deny",
          tool="rollback", target_environment="qa"),
]


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s) (the authoritative read-back):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _print_findings(status: dict) -> None:
    """Surface the gate's self-verification findings, split blocking vs warning.

    A blocking (HIGH) finding is a real structural-soundness problem; a warning is
    advisory (non-blocking — enforcement is verified by the suite). This policy now
    compiles finding-free; the split is kept defensively so any future advisory is
    surfaced rather than hidden.
    """
    findings = status.get("findings") or []
    high = [f for f in findings if f.get("severity") not in ("warning", "info")]
    warn = [f for f in findings if f.get("severity") in ("warning", "info")]
    print(f"  Gate self-verification: {len(findings)} finding(s) "
          f"({len(high)} blocking, {len(warn)} warning)")
    for f in high:
        print(f"    !! {f.get('severity')} {f.get('check')} -> {f.get('control')}")
    for f in warn:
        print(f"    ~  {f.get('severity')} {f.get('check')} -> {f.get('control')} "
              f"(non-blocking; enforcement verified by the suite)")
    if not findings:
        print("    (none — compiled clean and passed the gate's own probes)")


def _print_inputs(status: dict) -> None:
    inputs = status.get("input_fields") or []
    if not inputs:
        print("  No declared input fields: the gate constrains whatever the action "
              "proposes.")
        return
    print(f"  Input contract — supply each on every action ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        enum = spec.get("enum_values")
        enum_s = f" one of {enum}" if enum else ""
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}{enum_s}")


def _print_certificate(verdict: dict, expected: str) -> None:
    """Print the verdict's PROOF CERTIFICATE — the engine's OUTPUT.

    These fields demonstrate the RESULT; they do not reveal the kernel/Lean
    formalisation that produced them.
    """
    decision = verdict.get("decision")
    mark = "[OK]" if decision == expected else f"[!! expected {expected}]"
    print(f"    decision:       {str(decision).upper()}  {mark}")
    print(f"    permitted:      {verdict.get('permitted')}")
    print(f"    proof_checked:  {verdict.get('proof_checked')}")
    if verdict.get("deciding_rule"):
        print(f"    deciding_rule:  {verdict.get('deciding_rule')}")
    if verdict.get("denied_reason"):
        print(f"    denied_reason:  {verdict.get('denied_reason')}")
    if verdict.get("proof_summary"):
        print(f"    proof_summary:  {verdict.get('proof_summary')}")


def run_cicd_gate_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the CI/CD deployment policy (English in)")
    print(f"  POLICY:\n    {POLICY}\n")

    try:
        result = api.agent_policy.author(POLICY)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability), or your credentials lack write authority "
                  "over an existing org gate — skipping.")
            return
        raise

    platform = result.get("platform") or {}
    platform_id = platform.get("id")
    print(f"  Authored verified policy -> platform {platform_id} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)

    print_section(2, 3, "Reviewing the declared input fields + gate self-verification")
    status = api.agent_policy.status()
    _print_inputs(status)
    _print_findings(status)

    print_section(3, 3, "Gating proposed deploy actions (each verdict is proof-carrying)")
    passed = 0
    for label, action_args, expected in SUITE:
        print(f"\n  {'-' * 66}\n  {label}")
        verdict = api.agent_policy.authorize_action(
            platform_id, tool=action_args["tool"], args=action_args)
        _print_certificate(verdict, expected)
        passed += verdict.get("decision") == expected

    print(f"\n{passed}/{len(SUITE)} cases decided as expected.")
    print("\nDone. Each verdict above is proof-carrying: a permit means the kernel "
          "certified the action satisfies every policy requirement; a deny means it "
          "could NOT, fail-closed, naming the requirement that failed. Separation of "
          "duties (approver != author) is proved as a cross-field inequality — no "
          "discharge fact to supply. This PER-ACTION gate expresses the two "
          "time-flavoured rules (change window, review-before-merge) as "
          "caller-supplied booleans; for a NATIVE happens-before obligation proved "
          "from the session's ordered ledger, see "
          "40_agent_policy_gate_temporal.py (and the module docstring).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Policy Gate (CI/CD) — AmberTrace AI verified per-action "
                    "governance for a software-supply-chain deploy agent "
                    "(English-authored, proof-carrying permit/deny)",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_cicd_gate_demo, args)


if __name__ == "__main__":
    main()
