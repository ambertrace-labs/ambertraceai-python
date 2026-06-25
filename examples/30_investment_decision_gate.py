"""30 — Agent Policy Gate: investment decision-process gate (proof-carrying).

Proves that an AI investment agent FOLLOWED A DEFINED DECISION PROCESS before any
trade is allowed to stand. An untrusted execution agent proposes buy / sell trades;
Ambertrace compiles the English policy to a verified policy and PROVES every
proposed action permit/deny against it — fail-closed, with a machine-checked proof
that becomes the decision's audit record. The LLM only *proposes*; the kernel
*proves*.

Companion to 27 (single-action clinical-triage) and 28 (CI/CD deploy gate). This
one is the strongest *vertical* story: a fiduciary investment decision process,
grounded in a public, citable code of conduct.

THE FRAMEWORK (public, citable)
-------------------------------
The decision process is modelled on the globally-recognised CFA Institute *Code of
Ethics and Standards of Professional Conduct* — a code of ethics at the centre, with
duties that every investment decision must satisfy:

  - III(C) Suitability ......... the action must fit the client's stated risk profile
  - III(A) Loyalty/Prudence/Care + mandate ... within the client's permitted universe
  - V(A) Diligence & Reasonable Basis ........ adequate research must be on record
  - VI(A) Disclosure of Conflicts ............ conflicts must be disclosed
  - II Integrity of Capital Markets .......... no trading a restricted-list instrument
  - IV(C) Responsibilities of Supervisors .... a material trade needs an independent
                                               approver (separation of duties)
  - V(C) Record Retention .................... the proof certificate IS the record

(See https://www.cfainstitute.org/standards/professionals/code-ethics-standards .)

Synthetic/illustrative encoding of the CFA Code & Standards — not investment advice,
not a compliance product, not affiliated with or endorsed by CFA Institute.

WHAT THIS DEMONSTRATES
----------------------
An untrusted investment execution agent proposes buy / sell trades; the gate proves
each permit/deny against the English policy, fail-closed, with a proof. The policy
uses **tier-partitioned conditional permits** — the ``trade_tier`` enum (standard |
material) is the mutually-exclusive partition, exactly like 28's ``target_environment``
(dev/staging vs production). A standard-tier trade needs the suitability + diligence +
conflicts checks within a 5% cap; a material-tier trade allows up to a 10% cap but
additionally needs an independent approver (the approver must not be the recommender,
a cross-field inequality / separation of duties) — plus enum allowlists (action type,
instrument class, trade tier), a cross-field suitability comparison (instrument risk
must not exceed the client's risk tolerance), a concentration cap, and a restricted-
list block.

SEPARATION OF DUTIES (cross-field inequality — material tier only)
------------------------------------------------------------------
A material trade carries an independent-approver control: "the approver is not the
recommender" — a cross-field inequality between two action fields. It composes
correctly with the per-tier conditional permits: the *same* material 8% trade
PERMITS with approver != recommender and DENIES with approver == recommender. The
gate proves the inequality directly — there is no ``*_check_passed`` discharge fact
to supply. (recommend / hold actions are a natural extension; this example keeps the
single buy/sell action shape so the permits share one partition and compile cleanly —
two "only when" rules on the SAME tier compile to a vacuous permit; the enum
partition avoids that.)

A cosmetic caveat: the gate's self-check emits 2 ``warning``-severity
``V6_intent_CONSTRAINT_UNDECLARED_FIELD`` items on the ``position_pct`` caps — it
misclassifies the literal cap (5 / 10) as a cross-field reference. These are FALSE
POSITIVES; the caps demonstrably enforce (a standard 8% trade denies, a material 15%
denies, a material 9% permits). Treat ``warning``-severity findings as non-blocking.
(Declaring a ``position_pct`` range in the policy did NOT help — it flipped the gate
to ``V2_permit_all`` — so the field is left undeclared-range and the warnings are
handled as non-blocking; if the self-check refinement lands, these two warnings drop
to zero with no behavioural change.)

WHY IT MATTERS
--------------
The same properties that make an investment process auditable for a human make it
delegable to an AI: every decision is checked against the codified rules (not the
model's discretion), ships a proof certificate (the contemporaneous justification a
fiduciary must be able to produce), and fail-closes (an action that can't be proven
suitable + within-mandate + diligent + conflict-free is refused, never executed).

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. Authoring REPLACES the org's
single agent-policy gate. The Agent Policy Gate is a preview capability
(feature-flagged server-side); when it is not enabled — or your credentials lack
write authority over an existing org gate — ``author`` returns 404, which this demo
reports cleanly and skips.

Run with --help for options.

    python 30_investment_decision_gate.py
    python 30_investment_decision_gate.py -v
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# TIER-PARTITIONED conditional permits + SEPARATION OF DUTIES. The trade_tier enum
# (standard | material) is the mutually-exclusive partition — exactly like 28's
# target_environment (dev/staging vs production). A standard-tier trade clears on the
# core fiduciary checks within a 5% cap; a material-tier trade allows up to a 10% cap
# but must additionally carry an independent approver (approver != recommender, IV(C)).
# The tier partition keeps the permits non-overlapping so they compile cleanly (two
# "only when" rules on the SAME tier compile to a vacuous permit; the enum partition
# avoids that).
POLICY = (
    "An investment execution agent proposes buy or sell trades. "
    "Each action has a tool, an instrument_class, a trade_tier, an integer "
    "instrument_risk_level, an integer client_risk_tolerance, an integer position_pct, a "
    "recommender, an approver, and the boolean flags diligence_completed, "
    "suitability_assessed, conflicts_disclosed, and on_restricted_list. "
    "Only allow actions whose tool is buy or sell. "
    "Deny any action whose instrument_class is not equity, fixed_income, cash, or fund. "
    "Deny any action whose trade_tier is not standard or material. "
    "Deny any action when on_restricted_list is true. "
    "Permit a buy or sell action whose trade_tier is standard only when diligence_completed "
    "is true, suitability_assessed is true, conflicts_disclosed is true, the "
    "instrument_risk_level does not exceed the client_risk_tolerance, and the position_pct is at "
    "most 5. "
    "Permit a buy or sell action whose trade_tier is material only when diligence_completed "
    "is true, suitability_assessed is true, conflicts_disclosed is true, the "
    "instrument_risk_level does not exceed the client_risk_tolerance, the position_pct is at most "
    "10, and the approver is not the recommender."
)

# A fully-compliant, small, suitable, standard-tier buy; each case below flips one fact.
GOOD = {
    "tool": "buy", "instrument_class": "equity", "trade_tier": "standard",
    "instrument_risk_level": 3, "client_risk_tolerance": 4, "position_pct": 4,
    "recommender": "analyst_amy", "approver": "pm_ben",
    "diligence_completed": True, "suitability_assessed": True,
    "conflicts_disclosed": True, "on_restricted_list": False,
}


def _case(label: str, expected: str, **overrides) -> tuple[str, dict, str]:
    args = dict(GOOD)
    args.update(overrides)
    return label, args, expected


# (label, args, expected_decision) — the separation-of-duties pair (material 8% with
# approver != recommender PERMITS, == recommender DENIES) is the interesting tell.
SUITE = [
    _case("standard-tier suitable buy (4%, all checks)", "permit"),
    _case("standard-tier suitable sell, 3%", "permit", tool="sell", position_pct=3),
    _case("unsuitable: instrument risk 5 > client tolerance 4", "deny",
          instrument_risk_level=5),
    _case("no diligence / reasonable basis", "deny", diligence_completed=False),
    _case("conflict not disclosed", "deny", conflicts_disclosed=False),
    _case("instrument on the restricted list", "deny", on_restricted_list=True),
    _case("outside mandate: instrument_class 'crypto'", "deny",
          instrument_class="crypto"),
    _case("invalid trade_tier 'speculative'", "deny", trade_tier="speculative"),
    _case("forbidden tool 'short_naked' (action-type allowlist)", "deny",
          tool="short_naked"),
    # standard tier caps at 5%; an 8% standard trade must fail (wrong tier for the size)
    _case("standard-tier buy 8% (> 5% standard cap)", "deny", position_pct=8),
    # material tier: up to 10% BUT requires an independent approver (separation of duties)
    _case("material-tier buy 8% with independent approver (approver != recommender)",
          "permit", trade_tier="material", position_pct=8,
          recommender="analyst_amy", approver="pm_ben"),
    _case("material-tier buy 8% but approver == recommender (separation-of-duties)",
          "deny", trade_tier="material", position_pct=8,
          recommender="analyst_amy", approver="analyst_amy"),
    _case("material-tier 15% (> 10% concentration cap)", "deny",
          trade_tier="material", position_pct=15, approver="pm_ben"),
    _case("material-tier suitable buy 9% (independent approver)", "permit",
          trade_tier="material", position_pct=9, approver="pm_ben"),
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
    advisory. The ``position_pct`` caps draw 2 cosmetic
    ``V6_intent_CONSTRAINT_UNDECLARED_FIELD`` *warnings* (a literal cap misread as a
    cross-field operand) — non-blocking; enforcement is verified by the suite.
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


def run_investment_gate_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the investment decision-process policy (English in)")
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

    print_section(3, 3, "Gating proposed investment actions (each verdict is proof-carrying)")
    passed = 0
    for label, action_args, expected in SUITE:
        print(f"\n  {'-' * 66}\n  {label}")
        verdict = api.agent_policy.authorize_action(
            platform_id, tool=action_args["tool"], args=action_args)
        _print_certificate(verdict, expected)
        passed += verdict.get("decision") == expected

    print(f"\n{passed}/{len(SUITE)} cases decided as expected.")
    print("\nDone. Each verdict above is proof-carrying: a permit means the kernel "
          "certified the action satisfies every policy requirement (suitable + "
          "within-mandate + diligent + conflict-free, within the tier's cap); a deny "
          "means it could NOT, fail-closed, naming the requirement that failed. "
          "Separation of duties (approver != recommender) on the material tier is "
          "proved as a cross-field inequality — no discharge fact to supply.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Agent Policy Gate (investment) — AmberTrace AI verified per-action "
                    "governance for an AI investment execution agent, proving a "
                    "fiduciary decision process (English-authored, proof-carrying "
                    "permit/deny). Synthetic/illustrative CFA Code & Standards encoding "
                    "— not investment advice, not affiliated with CFA Institute.",
    )
    add_common_args(parser)
    args = parser.parse_args()
    run_demo(run_investment_gate_demo, args)


if __name__ == "__main__":
    main()
