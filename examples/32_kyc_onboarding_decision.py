"""32 — KYC Onboarding Decision PDP.

Verified proof-carrying KYC / customer-onboarding domain: a classify-then-
conclude policy chain that screens applicants and returns approve / edd
(enhanced due diligence) / reject decisions with machine-checked proofs. Each
application is supplied as structured facts; conclusions are read from the
certified symbolic trace.

  1. Create domain (names the boolean classifications)
  2. Upload KYC-application data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Decide showcase applications — structured facts → checked proof per decision

Creates resources on your account. Run with --help for options.

    python 32_kyc_onboarding_decision.py
    python 32_kyc_onboarding_decision.py --standard   # skip verified profile
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

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
DEFAULT_DATASET = DATA_DIR / "kyc_applications.csv"

DOMAIN_NAME = "KYC Onboarding Decision PDP"
DOMAIN_DESCRIPTION = (
    "Know-Your-Customer (KYC) onboarding Policy Decision Point (PDP) for evaluating customer "
    "applications. Each application has a customer type (retail or business), an id-verified "
    "flag, an address-verified flag, a PEP flag, a sanctions-hit flag, an adverse-media flag, "
    "a source-of-funds-documented flag, a risk score from 0 to 100, and an expected monthly "
    "volume. "
    "Classify these named conditions: an applicant is high-risk when its risk score is at "
    "least 75; an applicant is sanctioned when its sanctions-hit flag is set. "
    "Decide approve, edd, or reject by the first matching rule: reject for a sanctioned "
    "applicant; reject when the id-verified flag is not set; require enhanced due diligence "
    "(edd) for a PEP applicant; require edd for adverse media; require edd for a high-risk "
    "applicant; require edd when source of funds is not documented and the expected monthly "
    "volume is above 50000; otherwise approve. Every decision must be auditable."
)

_REJECT = {
    "Flag Is Sanctioned Equals Value",
    "Flag Id Verified Not Equals Value",
}
_EDD = {
    "Flag Pep Flag Equals Value",
    "Flag Adverse Media Equals Value",
    "Flag Is High Risk Equals Value",
    "Flag Source Of Funds Documented Not Equals Value",
    "Check Expected Monthly Volume Above Threshold",
}

SHOWCASE_APPLICATIONS = [
    ("sanctions hit (must reject)", {
        "customer_type": "business", "id_verified": True, "address_verified": True,
        "pep_flag": False, "sanctions_hit": True, "adverse_media": False,
        "source_of_funds_documented": True, "risk_score": 40,
        "expected_monthly_volume": 20000}),
    ("identity not verified (reject)", {
        "customer_type": "retail", "id_verified": False, "address_verified": False,
        "pep_flag": False, "sanctions_hit": False, "adverse_media": False,
        "source_of_funds_documented": True, "risk_score": 30,
        "expected_monthly_volume": 5000}),
    ("PEP with adverse media (edd)", {
        "customer_type": "business", "id_verified": True, "address_verified": True,
        "pep_flag": True, "sanctions_hit": False, "adverse_media": True,
        "source_of_funds_documented": True, "risk_score": 55,
        "expected_monthly_volume": 30000}),
    ("clean low-risk retail applicant (approve)", {
        "customer_type": "retail", "id_verified": True, "address_verified": True,
        "pep_flag": False, "sanctions_hit": False, "adverse_media": False,
        "source_of_funds_documented": True, "risk_score": 22,
        "expected_monthly_volume": 8000}),
]
SPARSE_APPLICATION = {"sanctions_hit": True, "customer_type": "business",
                      "id_verified": True}


def _decide(report: dict) -> tuple[str, list[str]]:
    fired = {r.get("rule_name") for r in symbolic_rules(report) if r.get("fired")}
    blocked = [
        r.get("rule_name") for r in symbolic_rules(report)
        if r.get("fired") and r.get("action_type") == "block"
    ]
    reject = sorted((fired & _REJECT) | set(blocked))
    if reject:
        return "reject", reject
    edd = sorted(fired & _EDD)
    if edd:
        return "edd", edd
    return "approve", []


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nAPPLICATION: {label}")
    try:
        report = api.platforms.query(
            platform_id, query="Should this applicant be onboarded?", facts=facts
        )
    except Exception as exc:
        print(f"  VERIFIED FAIL-SAFE — refused to certify (no decision returned): {exc}")
        print("=" * 70)
        return
    verdict, rules = _decide(report)
    print(f"  Decision: {verdict.upper()}" + (f"  ({', '.join(rules)})" if rules else ""))
    print(f"  proof_checked: {report.get('proof_checked')}")
    print(f"  {report.get('proof_summary')}")
    print("=" * 70)


def run_kyc_onboarding_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/kyc_applications.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating KYC onboarding PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading KYC-application data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology (classify-then-conclude chain)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(4, total, "Building verified platform")
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard,
        verified_min_confidence=args.tau,
    )
    profile = "verified" if platform.get("verified_profile") else "standard"
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')}, {profile})")

    print_section(5, total, "Deciding applications (structured facts → checked proof)")
    for label, facts in SHOWCASE_APPLICATIONS:
        _show(api, platform["id"], label, facts)
    _show(api, platform["id"], "sparse application (sanctions/type/id only)", SPARSE_APPLICATION)

    print(f"\nDone. Platform {platform['id']} is live. "
          "Verdicts are read from the certified symbolic trace (illustrative held-out: "
          "~95% three-way accuracy, 100% certification).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="KYC Onboarding Decision PDP — AmberTrace AI verified decision demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_kyc_onboarding_demo, args)


if __name__ == "__main__":
    main()
