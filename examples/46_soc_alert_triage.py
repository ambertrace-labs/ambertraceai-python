"""46 — SOC Alert Triage.

Verified proof-carrying SOC (security operations center) decision support:
compiles incoming security alerts and triages each one to auto_close / monitor /
escalate (escalate = route to a human analyst). The platform never takes
autonomous action — its role is auditable, proof-carrying decision support with
an analyst in the loop.

  1. Create domain (names the boolean classifications)
  2. Upload features-only alert data + build ontology
  3. Build a verified platform (τ = 0.6)
  4. Triage alerts from structured facts → checked proof per decision

Creates resources on your account. Run with --help for options.

    python 46_soc_alert_triage.py
    python 46_soc_alert_triage.py --standard   # skip verified profile
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
DEFAULT_DATASET = DATA_DIR / "soc_alerts.csv"

DOMAIN_NAME = "SOC Alert Triage"
DOMAIN_DESCRIPTION = (
    "Security-operations-center alert identification and triage decision support for handling "
    "incoming security alerts. Each alert has a source (edr, siem, ids, or email_gw), a severity "
    "(low, medium, high, or critical), an asset_criticality from 1 to 4, a known-false-positive "
    "flag, a threat-intel-match flag, a user-privileged flag, an off-hours flag, a repeated_count, "
    "and an mfa-anomaly flag. "
    "Classify these named conditions: an alert is a known false positive when its "
    "known_false_positive flag is set; an alert is critical-confirmed when it has a "
    "threat_intel_match and its asset_criticality is at least 3; an alert is a privileged-account "
    "anomaly when its user_privileged flag is set and its mfa_anomaly flag is set; an alert is "
    "noisy when its repeated_count is at least 5. "
    "Triage each alert by the first matching rule: auto_close a known false positive; escalate a "
    "critical-confirmed alert; escalate a privileged-account anomaly; monitor a high-or-critical "
    "severity alert otherwise; monitor a noisy alert; auto_close anything else. Every triage "
    "decision must be auditable, and critical-confirmed alerts must always be escalated to a human "
    "analyst and never suppressed."
)

_ESCALATE = {"Flag Is Critical Confirmed Equals Value",
             "Flag Is Privileged Account Anomaly Equals Value"}
_MONITOR = {"Check Severity Equals Value", "Flag Is Noisy Equals Value"}

SHOWCASE_ALERTS = [
    ("critical EDR, threat-intel match on criticality-4 asset (must escalate)", {
        "source": "edr", "severity": "critical", "asset_criticality": 4,
        "known_false_positive": False, "threat_intel_match": True, "user_privileged": False,
        "off_hours": True, "repeated_count": 1, "mfa_anomaly": False}),
    ("privileged user with MFA anomaly (must escalate)", {
        "source": "siem", "severity": "medium", "asset_criticality": 3,
        "known_false_positive": False, "threat_intel_match": False, "user_privileged": True,
        "off_hours": True, "repeated_count": 2, "mfa_anomaly": True}),
    ("known false positive (auto_close)", {
        "source": "email_gw", "severity": "low", "asset_criticality": 1,
        "known_false_positive": True, "threat_intel_match": False, "user_privileged": False,
        "off_hours": False, "repeated_count": 1, "mfa_anomaly": False}),
    ("low-severity noisy IDS alert, repeated_count 7 (monitor)", {
        "source": "ids", "severity": "low", "asset_criticality": 2,
        "known_false_positive": False, "threat_intel_match": False, "user_privileged": False,
        "off_hours": False, "repeated_count": 7, "mfa_anomaly": False}),
]


def _triage(report: dict) -> tuple[str, list[str]]:
    fired = {r.get("rule_name") for r in symbolic_rules(report) if r.get("fired")}
    esc = sorted(fired & _ESCALATE)
    if esc:
        return "escalate", esc
    mon = sorted(fired & _MONITOR)
    if mon:
        return "monitor", mon
    return "auto_close", []


def _show(api, platform_id: int, label: str, facts: dict) -> None:
    print(f"\n{'=' * 70}\nALERT: {label}")
    report = api.platforms.query(platform_id, query="Triage this alert.", facts=facts)
    level, rules = _triage(report)
    print(f"  Triage: {level.upper()}" + (f"  ({', '.join(rules)})" if rules else ""))
    print(f"  proof_checked: {report.get('proof_checked')}")
    print(f"  {report.get('proof_summary')}")
    print("=" * 70)


def run_soc_alert_triage_demo(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found. Expected at data/soc_alerts.csv",
              file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating SOC alert triage domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading alert data (features only)")
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

    print_section(5, total, "Triaging alerts (structured facts → checked proof)")
    for label, facts in SHOWCASE_ALERTS:
        _show(api, platform["id"], label, facts)

    print(f"\nDone. Platform {platform['id']} is live. "
          "Illustrative held-out: 98% three-way accuracy, 98% certification.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="SOC Alert Triage — AmberTrace AI verified security decision support demo",
    )
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_soc_alert_triage_demo, args)


if __name__ == "__main__":
    main()
