"""49 — Held-Out Evaluation Harness.

Operationalizes the "measured held-out: N% accuracy, M% certification" claims
the verified access-governance demos print. Loads labeled access requests,
replays each row as structured facts against a verified PDP platform, decodes
the permit/deny verdict from the certified symbolic trace, and scores it
against the ground-truth `decision` column. Verified queries that cannot be
certified are fail-closed (HTTP 503) and counted as refusals, never as wrong
answers.

  1. Create access-governance domain + upload data + build ontology
  2. Build a verified platform (τ = 0.6)
  3. Load the labeled CSV (training file, or a separate --holdout file)
  4. Replay each row → structured facts → checked proof → decoded verdict
  5. Report accuracy / certification-rate / fail-closed-rate

Creates resources on your account. Run with --help for options.

    python 49_evaluate_holdout.py
    python 49_evaluate_holdout.py --limit 100 -v
    python 49_evaluate_holdout.py --holdout data/access_requests.csv
    python 49_evaluate_holdout.py --standard   # skip verified profile
"""

from __future__ import annotations

import argparse
import csv
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
    run_demo,
    symbolic_rules,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "access_requests.csv"

DOMAIN_NAME = "Access Governance PDP (held-out eval)"
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

_DENY_CONCLUSIONS = {
    "Flag Clearance Level Below Threshold", "Flag Target Zone Equals Value",
    "Flag Is Privileged Request Equals Value", "Flag Is Restricted Zone Equals Value",
}

# Feature columns fed to the PDP as structured facts.
_INT_COLS = ("clearance_level", "device_posture_score", "target_sensitivity")
_BOOL_COLS = ("device_managed", "mfa_passed", "off_hours", "change_ticket")
_STR_COLS = ("requester_role", "source_zone", "target_zone", "access_type")

_TRUE = {"1", "yes", "true", "y", "t"}
_FALSE = {"0", "no", "false", "n", "f", ""}


def _parse_bool(raw: str) -> bool:
    value = (raw or "").strip().lower()
    if value in _TRUE:
        return True
    if value in _FALSE:
        return False
    raise ValueError(f"unrecognized boolean {raw!r}")


def _facts_from_row(row: dict[str, str]) -> dict:
    """Build a PDP facts dict from one labeled CSV row."""
    facts: dict = {}
    for col in _STR_COLS:
        facts[col] = (row.get(col) or "").strip()
    for col in _INT_COLS:
        facts[col] = int((row.get(col) or "0").strip())
    for col in _BOOL_COLS:
        facts[col] = _parse_bool(row.get(col, ""))
    return facts


def _decide(report: dict) -> str:
    """Decode permit/deny from the certified symbolic trace (cf. demo 18)."""
    denies = [
        r.get("rule_name") for r in symbolic_rules(report)
        if r.get("fired") and (r.get("action_type") == "block"
                               or r.get("rule_name") in _DENY_CONCLUSIONS)
    ]
    return "deny" if denies else "permit"


def _is_fail_closed(exc: AmbertraceError) -> bool:
    return getattr(exc, "status_code", None) == 503 or \
        getattr(exc, "code", "") == "service_unavailable"


def _load_rows(path: Path, limit: int) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = []
        for row in reader:
            rows.append(row)
            if len(rows) >= limit:
                break
    return rows


def run_holdout_eval_demo(api, args: argparse.Namespace) -> None:
    eval_path = args.holdout if args.holdout is not None else args.dataset
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/access_requests.csv",
              file=sys.stderr)
        sys.exit(1)
    if not eval_path.exists():
        print(f"ERROR: evaluation file {eval_path} not found", file=sys.stderr)
        sys.exit(1)
    total = 5

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

    print_section(3, total, f"Loading labeled rows (first {args.limit} of {eval_path.name})")
    in_sample = args.holdout is None
    if in_sample:
        print("  NOTE: evaluating against the SAME labeled file used to build the platform.")
        print("        These numbers are illustrative / IN-SAMPLE. Pass --holdout <file>")
        print("        with a separate labeled CSV for a true held-out measurement.")
    else:
        print(f"  Held-out file: {eval_path} (separate from the training CSV).")
    rows = _load_rows(eval_path, args.limit)
    print(f"  Loaded {len(rows)} rows.")

    print_section(4, total, "Replaying rows (structured facts → checked proof → verdict)")
    correct = 0
    evaluated = 0
    certified = 0
    fail_closed = 0
    for idx, row in enumerate(rows, start=1):
        request_id = row.get("request_id", f"row-{idx}")
        truth = (row.get("decision") or "").strip().lower()
        try:
            facts = _facts_from_row(row)
        except ValueError as exc:
            print(f"  [{idx}/{len(rows)}] {request_id}: SKIP (bad row: {exc})")
            continue
        try:
            report = api.platforms.query(
                platform["id"], query="Should this be permitted?", facts=facts)
        except AmbertraceError as exc:
            if _is_fail_closed(exc):
                fail_closed += 1
                if args.verbose:
                    print(f"  [{idx}/{len(rows)}] {request_id}: FAIL-CLOSED (refused to certify)")
                continue
            raise
        predicted = _decide(report)
        is_certified = report.get("proof_checked") is True
        evaluated += 1
        if is_certified:
            certified += 1
        hit = predicted == truth
        if hit:
            correct += 1
        if args.verbose:
            mark = "OK " if hit else "XX "
            cert = "certified" if is_certified else "uncertified"
            print(f"  [{idx}/{len(rows)}] {request_id}: pred={predicted} "
                  f"truth={truth} {mark}({cert})")
        elif idx % 10 == 0 or idx == len(rows):
            print(f"  ...processed {idx}/{len(rows)}")

    print_section(5, total, "Summary")
    n = len(rows)
    print(f"  Rows processed:     {n}")
    print(f"  Answers evaluated:  {evaluated}")
    print(f"  Fail-closed (503):  {fail_closed}")
    if evaluated:
        print(f"  Accuracy:            {correct}/{evaluated} = {correct / evaluated:.1%}")
        print(f"  Certification rate:  {certified}/{evaluated} = {certified / evaluated:.1%}")
    else:
        print("  Accuracy:            n/a (no answers evaluated)")
        print("  Certification rate:  n/a (no answers evaluated)")
    if n:
        print(f"  Fail-closed rate:    {fail_closed}/{n} = {fail_closed / n:.1%}")
    if in_sample:
        print("\n  Reminder: in-sample numbers above are illustrative, not a held-out claim.")

    print(f"\nDone. Platform {platform['id']} is live.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Held-out evaluation harness — AmberTrace AI verified PDP",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--holdout", type=Path, default=None,
                        help="Separate labeled CSV to evaluate against (default: the training CSV)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max rows to evaluate (default: 50)")
    args = parser.parse_args()
    run_demo(run_holdout_eval_demo, args)


if __name__ == "__main__":
    main()
