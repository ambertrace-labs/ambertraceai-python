"""29 — RF Resource Manager Conformance (verified interface conformance).

Demonstrates **interface conformance testing** of a message/service control
interface. Encode a specification's rules in plain English, evaluate observed
unit-under-test (UUT) exchanges against them, and return a certified
CONFORMANT / NON_CONFORMANT verdict carrying a machine-checked proof.

Standards analogue. This is the standard shape of interface conformance
testing (schema/version checks, mandatory-field and range checks, capacity and
pre-emption rules, a device state machine, latency bounds) expressed over
generic, public engineering concepts — it references **no** real specification,
product, identifier or version. "RF Resource Manager", "Device Manager" and the
state names are generic engineering terms.

  1. Create domain (names the conformance classifications)
  2. Upload features-only observed UUT exchanges + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Run conformance test cases from structured facts → checked proof per verdict

The uploaded ``rf_rm_conformance.csv`` is **features only** — uploading the
ground-truth ``expected_verdict`` column would make the build learn a trivial
label classifier instead of the conformance-policy chain. Booleans are emitted
as ``0/1`` in the CSV and coerced back to Python bools at query time. A verified
query that cannot be certified is fail-closed refused (HTTP 503); the showcase
reports that and continues rather than aborting.

The conformance verdict rides the platform's native ``permit``/``deny`` decision
vocabulary: a *permit* means every conformance rule was satisfied (CONFORMANT);
a *deny* means a rule fired against the exchange (NON_CONFORMANT). The
``_verdict_of`` helper maps the decision into CONFORMANT / NON_CONFORMANT at the
presentation layer.

Each query is printed in the standard seven-field conformance test-case format
(Purpose / Pre-conditions / Test steps / Test data / Expected result / Actual
result & status / Post-conditions), so the example reads as executable
conformance tests. The dataset is **synthetic and reproducible** (seeded;
``data/rf_rm_conformance.csv``); it carries no real specification data and is
safe to redistribute.

Creates resources on your account. Run with --help for options.

    python 29_rf_resource_manager_conformance.py
    python 29_rf_resource_manager_conformance.py --standard   # skip verified profile
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
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "rf_rm_conformance.csv"
DEFAULT_HOLDOUT = DATA_DIR / "rf_rm_conformance_holdout.csv"

DOMAIN_NAME = "RF Resource Manager Conformance"
DOMAIN_DESCRIPTION = (
    "Interface conformance testing of an RF Resource Manager control interface. Each "
    "record is one observed control exchange between a controller and the unit under "
    "test. Each exchange has a schema version (v1, v2, v3, v0, or v9), a component id "
    "(RRM-1, RRM-2, RRM-3, RRM-4, RRM-0, or UNREG-9), a boolean indicating whether all "
    "mandatory fields are present, a boolean indicating whether every field is within "
    "range, an integer requested capacity, an integer available capacity, a device "
    "state transitioned from (IDLE, INIT, or ACTIVE), a device state transitioned to "
    "(IDLE, INIT, or ACTIVE), a boolean indicating whether the initialisation health "
    "check passed, an integer request priority, an integer active allocation priority, "
    "a boolean indicating whether pre-emption was performed, an integer acknowledgement "
    "latency in milliseconds, and an integer acknowledgement latency limit in "
    "milliseconds. "
    "Classify these named conditions: the schema version is unknown when it is v0 or "
    "v9; the component id is unregistered when it is RRM-0 or UNREG-9; capacity is "
    "exceeded when the requested capacity is greater than the available capacity; the "
    "state transition is illegal when the device state transitioned from is IDLE and "
    "the device state transitioned to is IDLE, or the device state transitioned from is "
    "IDLE and the device state transitioned to is ACTIVE, or the device state "
    "transitioned from is INIT and the device state transitioned to is IDLE, or the "
    "device state transitioned from is INIT and the device state transitioned to is "
    "INIT, or the device state transitioned from is ACTIVE and the device state "
    "transitioned to is INIT, or the device state transitioned from is ACTIVE and the "
    "device state transitioned to is ACTIVE; an activation lacks its health check when "
    "the device state transitioned to is ACTIVE and the initialisation health check did "
    "not pass; pre-emption is missing when the request priority is greater than the "
    "active allocation priority and pre-emption was not performed; the acknowledgement "
    "latency is exceeded when the acknowledgement latency in milliseconds is greater "
    "than the acknowledgement latency limit in milliseconds. "
    "Decide permit or deny by the first matching rule: deny for unknown schema version "
    "when the schema version is unknown; deny for unregistered component when the "
    "component id is unregistered; deny for missing mandatory field when the mandatory "
    "fields are not all present; deny for field out of range when a field is not within "
    "range; deny for capacity exceeded when capacity is exceeded; deny for illegal state "
    "transition when the state transition is illegal; deny for activation without health "
    "check when an activation lacks its health check; deny for missing pre-emption when "
    "pre-emption is missing; deny for latency exceeded when the acknowledgement latency "
    "is exceeded; otherwise permit. Every decision must be auditable: a permit verdict "
    "means the exchange is conformant and a deny verdict means it is non-conformant."
)

QUERY = "Is this control exchange conformant?"

# A fully-conformant baseline exchange; each showcase case overrides one aspect.
_BASE = {
    "schema_version": "v2", "component_id": "RRM-1",
    "mandatory_fields_present": True, "field_in_range": True,
    "requested_capacity": 40, "available_capacity": 80,
    "device_state_from": "INIT", "device_state_to": "ACTIVE", "init_health_passed": True,
    "request_priority": 2, "active_allocation_priority": 4, "preemption_performed": True,
    "ack_latency_ms": 90, "ack_latency_limit_ms": 250,
}


def _facts(**overrides) -> dict:
    f = dict(_BASE)
    f.update(overrides)
    return f


# (purpose, rule_covered, facts, expected_verdict, expected_rule)
SHOWCASE = [
    ("Confirm a fully-compliant production exchange certifies as conformant.",
     "all rules satisfied", _facts(), "CONFORMANT", ""),
    ("A direct IDLE->ACTIVE skips INIT — only IDLE->INIT->ACTIVE->IDLE is permitted.",
     "Illegal State Transition",
     _facts(device_state_from="IDLE", device_state_to="ACTIVE"),
     "NON_CONFORMANT", "Illegal State Transition"),
    ("An allocation request for more than the available capacity must be rejected.",
     "Capacity Exceeded",
     _facts(requested_capacity=90, available_capacity=60),
     "NON_CONFORMANT", "Capacity Exceeded"),
    ("A device may reach ACTIVE only when the initialisation health check passed.",
     "Activation Without Health Check",
     _facts(device_state_from="INIT", device_state_to="ACTIVE", init_health_passed=False),
     "NON_CONFORMANT", "Activation Without Health Check"),
    ("A message carrying an unsupported schema version is non-conformant.",
     "Unknown Schema Version",
     _facts(schema_version="v9"),
     "NON_CONFORMANT", "Unknown Schema Version"),
    ("A higher-priority request must pre-empt a lower-priority active allocation.",
     "Missing Pre-emption",
     _facts(device_state_from="ACTIVE", device_state_to="IDLE",
            request_priority=5, active_allocation_priority=2, preemption_performed=False),
     "NON_CONFORMANT", "Missing Pre-emption"),
    ("The control acknowledgement latency must not exceed the stated limit.",
     "Latency Exceeded",
     _facts(ack_latency_ms=420, ack_latency_limit_ms=250),
     "NON_CONFORMANT", "Latency Exceeded"),
]

# CSV strings -> typed facts the engine expects (booleans are emitted as 0/1).
_coercers = {
    "mandatory_fields_present": lambda v: bool(int(v)),
    "field_in_range": lambda v: bool(int(v)),
    "init_health_passed": lambda v: bool(int(v)),
    "preemption_performed": lambda v: bool(int(v)),
    "requested_capacity": int, "available_capacity": int,
    "request_priority": int, "active_allocation_priority": int,
    "ack_latency_ms": int, "ack_latency_limit_ms": int,
}


def _verdict_of(report: dict) -> str:
    """Normalise the platform's decision into CONFORMANT / NON_CONFORMANT.

    The conformance verdict rides the platform's native permit/deny decision
    vocabulary: a *permit* means the exchange satisfied every conformance rule
    (CONFORMANT); a *deny* means a rule fired against it (NON_CONFORMANT).
    """
    dec = (report.get("decision") or "").strip().lower()
    if dec == "deny" or ("non" in dec and "conform" in dec):
        return "NON_CONFORMANT"
    if dec in ("permit", "allow") or "conform" in dec:
        return "CONFORMANT"
    return dec.upper() or "UNKNOWN"


def _query(api, platform_id: int, facts: dict):
    """Query, dropping empty/None facts (the verified engine fail-closes on those)."""
    query_facts = {k: v for k, v in facts.items() if v not in ("", None)}
    return api.platforms.query(platform_id, query=QUERY, facts=query_facts)


def _run_case(api, platform_id: int, n: int, purpose: str, rule: str,
              facts: dict, expected: str, expected_rule: str) -> bool:
    print(f"\n{'=' * 72}\nTEST CASE {n} — rule under test: {rule}")
    print(f"  Purpose:        {purpose}")
    print("  Pre-conditions: verified platform built; one UUT exchange captured.")
    print("  Test steps:     supply the captured facts and run the conformance query.")
    print(f"  Test data:      {facts}")
    print(f"  Expected result: {expected}"
          + (f" (rule: {expected_rule})" if expected_rule else ""))
    try:
        report = _query(api, platform_id, facts)
    except AmbertraceError as exc:
        reason = ""
        details = getattr(exc, "details", None)
        if details:
            reason = " — " + "; ".join(
                f"{d.get('field')}: {d.get('message')}"
                for d in details if isinstance(d, dict))
        print(f"  Actual result:  UNCERTIFIED — query fail-closed{reason}")
        print(f"  Status:         {'FAIL' if expected else 'n/a'}")
        return False
    verdict = _verdict_of(report)
    ok = verdict == expected
    print(f"  Actual result:  {verdict}  (proof_checked={report.get('proof_checked')})")
    print(f"  Status:         {'PASS' if ok else 'FAIL — verdict mismatch'}")
    print("  Post-conditions: proof-carrying Amber Report stored as evidence.")
    return ok


def _score_holdout(api, platform_id: int, holdout: Path, limit: int) -> None:
    if not holdout.exists():
        print(f"\n(No held-out file at {holdout}; skipping accuracy check.)")
        return
    with holdout.open() as f:
        rows = list(csv.DictReader(f))[:limit]
    feature_cols = [c for c in rows[0] if c not in ("expected_verdict", "expected_rule")]
    correct = certified = 0
    for r in rows:
        facts = {c: _coercers.get(c, lambda v: v)(r[c]) for c in feature_cols
                 if c != "exchange_id"}
        expected = r["expected_verdict"].strip().upper()
        try:
            report = _query(api, platform_id, facts)
        except AmbertraceError:
            continue  # fail-closed; neither correct nor certified
        if report.get("proof_checked"):
            certified += 1
        if _verdict_of(report) == expected:
            correct += 1
    n = len(rows)
    print(f"\n{'=' * 72}\nHELD-OUT CONFORMANCE CHECK ({n} unseen exchanges)")
    print(f"  Decision accuracy: {correct}/{n} ({100 * correct / n:.0f}%)")
    print(f"  Certified (proof_checked): {certified}/{n} ({100 * certified / n:.0f}%)")


def run_rf_rm_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/rf_rm_conformance.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating RF Resource Manager conformance domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading observed UUT exchanges (features only)")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (classify-then-conclude chain)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=16)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Running conformance test cases (facts → checked proof)")
    passed = 0
    for n, (purpose, rule, facts, expected, expected_rule) in enumerate(SHOWCASE, 1):
        passed += _run_case(api, platform["id"], n, purpose, rule,
                             facts, expected, expected_rule)
    print(f"\n{passed}/{len(SHOWCASE)} showcase test cases decided as expected.")

    if not args.no_holdout:
        _score_holdout(api, platform["id"], args.holdout, args.holdout_limit)

    print(f"\nDone. Platform {platform['id']} is live. Synthetic, reproducible conformance "
          "data; every certified verdict ships a proof-carrying Amber Report.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="RF Resource Manager Conformance — verified proof-carrying conformance tests",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--holdout", type=Path, default=DEFAULT_HOLDOUT)
    parser.add_argument("--holdout-limit", type=int, default=50,
                        help="number of held-out exchanges to score (default: 50)")
    parser.add_argument("--no-holdout", action="store_true",
                        help="skip the held-out accuracy check")
    args = parser.parse_args()
    run_demo(run_rf_rm_demo, args)


if __name__ == "__main__":
    main()
