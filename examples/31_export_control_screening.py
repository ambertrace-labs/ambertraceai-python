"""31 — Export-Control Screening PDP.

Verified proof-carrying export-control / sanctions-screening domain: a
classify-then-conclude policy chain that screens shipments and returns
permit / license_required / deny decisions with machine-checked proofs. Each
screening is supplied as structured facts; conclusions are read from the
certified symbolic trace.

  1. Create domain (names the boolean classifications)
  2. Upload export-screening data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Screen showcase shipments — structured facts → checked proof per decision

Creates resources on your account. Run with --help for options.

    python 31_export_control_screening.py
    python 31_export_control_screening.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "export_screenings.csv"

DOMAIN_NAME = "Export-Control Screening PDP"
DOMAIN_DESCRIPTION = (
    "Export-control and sanctions-screening Policy Decision Point (PDP) for evaluating "
    "shipments. Each screening has an ECCN, an item category, a destination country, a "
    "country group (A, B, D, or E), an end-user type (commercial, government, or military), "
    "an end use (civil, dual, or military), a denied-party-hit flag, a controlled-item flag, "
    "and a license-exception-eligible flag. "
    "Classify these named conditions: a party is a denied party when its denied-party-hit "
    "flag is set; a destination is embargoed when its country group is E; an item is "
    "controlled when its controlled-item flag is set. "
    "Decide permit, license_required, or deny by the first matching rule: deny for a denied "
    "party; deny for an embargoed destination; require a license for a controlled item with a "
    "military end use; require a license for a controlled item shipped to country group D "
    "without a license exception; otherwise permit. Every decision must be auditable."
)

_DENY = {
    "Flag Is Denied Party Equals Value",
    "Flag Is Embargoed Destination Equals Value",
}
_LICENSE = {
    "Flag Is Controlled Item Equals Value",
    "Check End Use Equals Value",
    "Check Country Group Equals Value",
    "Flag License Exception Eligible Equals Value",
}

SHOWCASE_SCREENINGS = [
    ("denied-party hit (must deny)", {
        "eccn": "5A002", "item_category": "telecom", "destination_country": "Germany",
        "country_group": "A", "end_user_type": "commercial", "end_use": "civil",
        "denied_party_hit": True, "controlled_item": True,
        "license_exception_eligible": True}),
    ("embargoed destination (group E)", {
        "eccn": "EAR99", "item_category": "electronics", "destination_country": "Iran",
        "country_group": "E", "end_user_type": "commercial", "end_use": "civil",
        "denied_party_hit": False, "controlled_item": False,
        "license_exception_eligible": True}),
    ("controlled dual-use to group D, no exception", {
        "eccn": "3A001", "item_category": "sensors", "destination_country": "China",
        "country_group": "D", "end_user_type": "commercial", "end_use": "dual",
        "denied_party_hit": False, "controlled_item": True,
        "license_exception_eligible": False}),
    ("clean commercial civil export to group A", {
        "eccn": "EAR99", "item_category": "materials", "destination_country": "Japan",
        "country_group": "A", "end_user_type": "commercial", "end_use": "civil",
        "denied_party_hit": False, "controlled_item": False,
        "license_exception_eligible": True}),
]
SPARSE_SCREENING = {"country_group": "E", "end_use": "civil",
                    "destination_country": "North Korea"}


def _decide(report: dict) -> tuple[str, list[str]]:
    fired = {r.get("rule_name") for r in symbolic_rules(report) if r.get("fired")}
    blocked = [
        r.get("rule_name") for r in symbolic_rules(report)
        if r.get("fired") and r.get("action_type") == "block"
    ]
    deny = sorted((fired & _DENY) | set(blocked))
    if deny:
        return "deny", deny
    lic = sorted(fired & _LICENSE)
    if lic:
        return "license_required", lic
    return "permit", []


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nSCREENING: {label}")
    try:
        report = api.platforms.query(
            platform_id, query="Can this shipment be exported?", facts=facts
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


def run_export_control_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/export_screenings.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating export-control screening PDP domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading export-screening data")
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

    print_section(5, total, "Screening shipments (structured facts → checked proof)")
    for label, facts in SHOWCASE_SCREENINGS:
        _show(api, platform["id"], label, facts)
    _show(api, platform["id"], "sparse screening (group/end-use/country only)", SPARSE_SCREENING)

    print(f"\nDone. Platform {platform['id']} is live. "
          "Verdicts are read from the certified symbolic trace (illustrative held-out: "
          "~96% three-way accuracy, 100% certification).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export-Control Screening PDP — AmberTrace AI verified decision demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_export_control_demo, args)


if __name__ == "__main__":
    main()
