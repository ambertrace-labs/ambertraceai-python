"""40 — Human-in-the-loop symbolic rule governance (suggest → review → approve).

The expert-in-the-loop loop for symbolic rules. A neurosymbolic platform can
PROPOSE human-readable rules from the data, but an expert stays in control: this
walkthrough suggests candidate rules, reviews them, APPROVES the good ones,
REJECTS the rest, and finally shows how an expert can DEACTIVATE an approved rule
(without deleting it) — the audit-friendly governance loop for regulated domains
like loan approval.

The six steps:
  1. Create a loan-approval domain + upload the loan applications CSV.
  2. Build the ontology.
  3. Build the platform (verified profile by default; --standard to skip it).
  4. Ask the platform to SUGGEST rules, poll the job, and list each candidate.
  5. APPROVE the first suggestion and REJECT the second (review decisions).
  6. List the rules, then DEACTIVATE the just-approved rule via update_rule —
     how an expert retires a rule without losing the audit trail.

Dataset: data/loan_applications.csv.

Creates resources on your account. Needs a user-scoped key (at_...): rule
suggestion + approval are WRITE operations. Run with --help for options.

    python 40_rule_review_loop.py
    python 40_rule_review_loop.py --standard --max-suggestions 5 -v
"""

from __future__ import annotations

import argparse
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
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "loan_applications.csv"

DOMAIN_NAME = "Loan Approval Rule Governance"
DOMAIN_DESCRIPTION = (
    "Consumer loan approval and risk assessment. Each application records the "
    "applicant's income, requested loan amount, credit score, debt-to-income "
    "ratio, and employment status. Decisions must be auditable and explainable: "
    "loans are approved or denied under transparent, expert-reviewed rules "
    "(income and credit-score thresholds, debt-to-income limits)."
)


def run_rule_review_demo(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Creating loan-approval domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology (generating entities & rules)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)

    print_section(3, total, "Building platform (knowledge graph + rule engine)")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(4, total, "Suggesting candidate rules (expert review queue)")
    suggestions: list[dict] = []
    try:
        run = api.platforms.suggest_rules(platform["id"], max_suggestions=args.max_suggestions)
        job_id = run.get("job_id") or (run.get("job") or {}).get("id")
        if job_id:
            api.wait_for_job(int(job_id), timeout=180)
            print("  Suggestion run finished.")
        suggestions = api.platforms.list_suggestions(platform["id"])
        print(f"  {len(suggestions)} suggestion(s) awaiting review:")
        for s in suggestions:
            print(f"    #{s.get('id')}: {s.get('description') or s.get('rule')}")
    except AmbertraceError as exc:
        print(f"  ! Rule suggestion unavailable ({exc.status_code} {exc.code}): {exc}")

    print_section(5, total, "Reviewing: approve the first, reject the second")
    approved_any = False
    try:
        if suggestions:
            first = suggestions[0]["id"]
            api.platforms.approve_suggestion(platform["id"], first)
            approved_any = True
            print(f"  APPROVED suggestion #{first} — it becomes an active rule.")
            if len(suggestions) > 1:
                second = suggestions[1]["id"]
                api.platforms.reject_suggestion(platform["id"], second)
                print(f"  REJECTED suggestion #{second} — discarded, not added.")
            else:
                print("  Only one suggestion — nothing to reject.")
        else:
            print("  No suggestions to review; skipping approve/reject.")
    except AmbertraceError as exc:
        print(f"  ! Review action unavailable ({exc.status_code} {exc.code}): {exc}")

    print_section(6, total, "Listing rules + deactivating one (without deleting)")
    try:
        rules = api.platforms.list_rules(platform["id"], include_inactive=True)
        print(f"  {len(rules)} rule(s) on the platform:")
        for r in rules:
            print(f"    #{r.get('id')} {r.get('name', '?')}  active={r.get('is_active')}")

        # Demonstrate update_rule: an expert retires the just-approved rule by
        # deactivating it — the rule stays on the platform for the audit trail.
        if approved_any and rules:
            active = [r for r in rules if r.get("is_active")]
            target = active[0] if active else rules[0]
            rid = target.get("id")
            print(
                f"\n  Deactivating rule #{rid} ({target.get('name', '?')}) — "
                f"before: is_active={target.get('is_active')}"
            )
            updated = api.platforms.update_rule(platform["id"], rid, is_active=False)
            print(f"  After:  is_active={updated.get('is_active')}")
            print("  An expert deactivates a rule (it stays for the audit trail) "
                  "rather than deleting it — reactivate any time with is_active=True.")
        else:
            print("  No approved rule to deactivate.")
    except AmbertraceError as exc:
        print(f"  ! Rule listing/update unavailable ({exc.status_code} {exc.code}): {exc}")

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Human-in-the-loop symbolic rule governance — AmberTrace AI demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: loan_applications.csv)",
    )
    parser.add_argument(
        "--max-suggestions", type=int, default=3,
        help="How many candidate rules to request (default: 3).",
    )
    args = parser.parse_args()
    run_demo(run_rule_review_demo, args)


if __name__ == "__main__":
    main()
