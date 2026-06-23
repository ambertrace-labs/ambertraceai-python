"""51 — Proof Anatomy.

A deep-dive that fully unpacks ONE verified response — a reference for exactly
what a proof-carrying answer contains. Queries the verified access-governance
PDP once with a complete, deny-worthy structured-fact request, then prints every
part of the report with explanatory prose: the query and answer, the
proof_checked flag and proof_summary, the confidence block (neural/symbolic
weights), the full symbolic trace rule by rule, and the certified vs
rejected-below-τ facts. This is what an auditor reads.

  1. Create access-governance domain + upload data + build ontology
  2. Build a verified platform (τ = 0.6)
  3. Query once with a complete deny-worthy structured-fact request
  4. Unpack and explain every section of the proof-carrying report

Creates resources on your account. Run with --help for options.

    python 51_proof_anatomy.py
    python 51_proof_anatomy.py --tau 0.7 -v
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_section,
    rules_evaluated_count,
    rules_fired_count,
    run_demo,
    symbolic_rules,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "access_requests.csv"

DOMAIN_NAME = "Access Governance PDP (proof anatomy)"
DOMAIN_DESCRIPTION = (
    "Access-governance Policy Decision Point (PDP) for evaluating access requests. "
    "Each request has a requester role, a clearance level from 1 to 4, whether the device "
    "is managed, a device posture score from 0 to 100, whether MFA passed, a source zone "
    "and a target zone, a target sensitivity from 1 to 4, an access type, an off-hours flag, "
    "and a change-ticket flag. "
    "Classify these named conditions: a device is trusted when it is managed and its posture "
    "score is at least 70; a request is privileged when the access type is write or admin, or "
    "the target sensitivity is at least 3; a target zone is restricted when it is the restricted "
    "zone or the ot_network zone. "
    "Decide permit or deny by the first matching rule: deny for untrusted device when the target "
    "zone is restricted and the device is not trusted; deny for mfa required when the request is "
    "privileged and MFA did not pass; deny for insufficient clearance when the clearance level is "
    "below the target sensitivity; deny for change control when the target zone is ot_network and "
    "there is no change ticket; otherwise permit. Every decision must be auditable."
)

# A complete, clearly deny-worthy request: untrusted device → ot_network.
DENY_REQUEST = {
    "requester_role": "contractor", "clearance_level": 2, "device_managed": False,
    "device_posture_score": 40, "mfa_passed": False, "source_zone": "guest",
    "target_zone": "ot_network", "target_sensitivity": 4, "access_type": "admin",
    "off_hours": False, "change_ticket": False,
}


def _is_fail_closed(exc: AmbertraceError) -> bool:
    return getattr(exc, "status_code", None) == 503 or \
        getattr(exc, "code", "") == "service_unavailable"


def _unpack(report: dict) -> None:
    explanation = report.get("explanation", {}) or {}

    print(f"\n{'=' * 70}")
    print("PROOF-CARRYING REPORT — section by section")
    print("=" * 70)

    # --- The question and the answer ----------------------------------------
    print("\n[query] The exact question the engine answered:")
    print(f"  {report.get('query')}")
    print("\n[answer] The natural-language decision returned to the caller:")
    print(f"  {(report.get('answer') or '')[:300]}")

    # --- The proof flag -----------------------------------------------------
    print("\n[proof_checked] Whether a machine-checked proof backs this answer.")
    print("  True means the symbolic engine derived the conclusion from certified")
    print("  facts and the proof was verified end to end — not merely asserted.")
    print(f"  proof_checked = {report.get('proof_checked')}")
    if report.get("proof_summary"):
        print("\n[proof_summary] Human-readable summary of what was proven:")
        print(f"  {report.get('proof_summary')}")

    # --- Confidence block ---------------------------------------------------
    confidence = explanation.get("confidence", {}) or {}
    print("\n[confidence] How the overall confidence splits across the two engines.")
    print("  A verified answer leans on the symbolic side; neural retrieval only")
    print("  supplies context. The weights show how each contributed.")
    print(f"  overall:  {confidence.get('overall', 0.0):.0%}")
    print(f"  neural:   {confidence.get('neural_confidence', 0.0):.0%}"
          f"  (weight {confidence.get('neural_weight', 0.0)})")
    print(f"  symbolic: {confidence.get('symbolic_confidence', 0.0):.0%}"
          f"  (weight {confidence.get('symbolic_weight', 0.0)})")

    # --- Symbolic trace -----------------------------------------------------
    rules = symbolic_rules(report)
    fired = rules_fired_count(report)
    evaluated = rules_evaluated_count(report)
    print(f"\n[symbolic_trace] The policy rules the engine evaluated ({fired}/{evaluated} fired).")
    print("  Every fired rule is a step in the proof; an auditor can replay each one")
    print("  against the certified facts. 'block' actions are the deny conclusions.")
    if rules:
        for rule in rules:
            status = "FIRED" if rule.get("fired") else "not fired"
            action = f" [{rule['action_type']}]" if rule.get("action_type") else ""
            marker = ">>>" if rule.get("fired") else "   "
            print(f"  {marker} {rule.get('rule_name')} ({rule.get('rule_type')}): "
                  f"{status}{action}")
    else:
        print("  (no rules in trace)")

    # --- Certified vs rejected facts ----------------------------------------
    print("\n[facts] Which inputs cleared the certification threshold τ.")
    print("  Facts at or above τ are certified and admissible in the proof; facts")
    print("  below τ are rejected so an uncertain input can never drive a decision.")
    certified_facts = explanation.get("certified_facts")
    rejected_facts = explanation.get("rejected_facts")
    if certified_facts is not None:
        print(f"  certified_facts: {certified_facts}")
    else:
        print("  certified_facts: (not reported)")
    if rejected_facts:
        print(f"  rejected_facts (below τ): {rejected_facts}")
    else:
        print("  rejected_facts (below τ): none")

    print("\n" + "=" * 70)
    print("An auditor can: read the decision (answer), confirm it is proof-backed")
    print("(proof_checked/proof_summary), see which engine carried it (confidence),")
    print("replay each fired rule (symbolic_trace), and verify only certified facts")
    print("(facts) were admitted. That is a complete, reproducible audit trail.")
    print("=" * 70)


def run_proof_anatomy_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 4

    print_section(1, total, "Creating access-governance PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(2, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(3, total, "Querying once (complete deny-worthy request)")
    print(f"  facts: {DENY_REQUEST}")
    try:
        report = api.platforms.query(
            platform["id"], query="Should this be permitted?", facts=DENY_REQUEST)
    except AmbertraceError as exc:
        if _is_fail_closed(exc):
            print(f"\n  VERIFIED FAIL-CLOSED — the engine refused to certify a result "
                  f"(no proof to unpack). ({exc})")
            print(f"\nDone. Platform {platform['id']} is live.")
            return
        raise

    print_section(4, total, "Unpacking the proof-carrying report")
    _unpack(report)

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Proof Anatomy — AmberTrace AI proof-carrying answer deep-dive",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_proof_anatomy_demo, args)


if __name__ == "__main__":
    main()
