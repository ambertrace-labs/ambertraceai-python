"""17 — Vehicle Inspection Rule Coverage Experiment.

Builds a vehicle-inspection platform, then runs a battery of queries that
each carry a pre-registered prediction about whether a symbolic rule will
fire. The domain combines numeric thresholds (tyre tread >= 1.6mm, brake
efficiency >= 58%), cross-field comparisons (emissions vs limit), and
string/boolean checks (MOT status, insurance active).

After running, the demo scores predictions against the rules that actually
fired — a compact regression test for the symbolic engine.

Creates resources on your account. Run with --help for options.

    python 16_rule_coverage.py
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_quality,
    print_section,
    rules_evaluated_count,
    rules_fired_count,
    run_demo,
    symbolic_rules,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "vehicle_inspections.csv"

DOMAIN_NAME = "Vehicle Inspection Compliance"
DOMAIN_DESCRIPTION = (
    "Vehicle roadworthiness inspection and compliance checking. "
    "The domain enforces the following rules: "
    "vehicles must have a valid MOT certificate (mot_status must be 'valid'); "
    "vehicles must have active insurance (insurance_active must be Yes); "
    "tyre tread depth must be at least 1.6mm for cars and vans, "
    "or at least 1.0mm for motorcycles "
    "(tyre_tread_mm must be greater than or equal to tyre_minimum_mm); "
    "brake efficiency must meet the minimum threshold "
    "(brake_efficiency_pct must be greater than or equal to brake_minimum_pct); "
    "CO2 emissions must not exceed the vehicle type limit "
    "(emissions_co2_gkm must be less than or equal to emissions_limit_co2_gkm); "
    "vehicles over 15 years old require enhanced inspection; "
    "all inspection decisions must be recorded and auditable."
)

PREDICTION_QUERIES = [
    (
        "A vehicle is 16 years old. Does it require enhanced inspection?",
        "WILL_FIRE",
        "Numeric threshold with explicit value — highest reliability rule type",
    ),
    (
        "A car has tyre tread depth of 1.4mm. The minimum required is 1.6mm. "
        "Does this vehicle pass the tyre inspection?",
        "WILL_FIRE",
        "Explicit numeric comparison — same pattern as age thresholds",
    ),
    (
        "A car has CO2 emissions of 155 g/km. The emissions limit for this "
        "vehicle type is 130 g/km. Does it pass the emissions test?",
        "WILL_FIRE",
        "Cross-field numeric comparison",
    ),
    (
        "A vehicle has an expired MOT certificate. Can it pass inspection?",
        "WONT_FIRE",
        "String equality check from natural language — historically unreliable",
    ),
    (
        "A vehicle has no active insurance. Is it roadworthy?",
        "WONT_FIRE",
        "Boolean from natural language",
    ),
    (
        "A vehicle has brake efficiency of 48%. The minimum required is 58%. "
        "Does it pass the brake test?",
        "WILL_FIRE",
        "Explicit numeric comparison with values stated in query",
    ),
    (
        "Evaluate a 3-year-old car with valid MOT, active insurance, "
        "CO2 emissions 110 g/km (limit 130), tyre tread 5.5mm (minimum 1.6mm), "
        "and brake efficiency 79% (minimum 58%). Is it roadworthy?",
        "PARTIAL",
        "Audit catch-all will fire; specific pass rules uncertain",
    ),
    (
        "A car has CO2 emissions of 131 g/km against a limit of 130 g/km. "
        "It exceeds the limit by just 1 g/km. Does it fail?",
        "UNCERTAIN",
        "Tests real numeric comparison vs keyword pattern matching",
    ),
]


def evaluate_report(report: dict[str, Any], prediction: str, reasoning: str) -> str:
    rules = symbolic_rules(report)
    targeted_fired = [
        r
        for r in rules
        if r.get("fired")
        and "audit" not in (r.get("rule_name") or "").lower()
        and "explainable" not in (r.get("rule_name") or "").lower()
    ]
    total_fired = rules_fired_count(report)

    if targeted_fired:
        actual = "FIRED"
    elif total_fired > 0:
        actual = "PARTIAL (audit/derive only)"
    else:
        actual = "NOT_FIRED"

    if prediction == "UNCERTAIN":
        verdict = "OBSERVED"
    elif (
        (prediction == "WILL_FIRE" and actual == "FIRED")
        or (prediction == "WONT_FIRE" and actual in ("NOT_FIRED", "PARTIAL (audit/derive only)"))
        or (prediction == "PARTIAL" and actual in ("PARTIAL (audit/derive only)", "FIRED"))
    ):
        verdict = "CORRECT"
    else:
        verdict = "WRONG"

    print(f"\n{'=' * 70}")
    print("RULE-COVERAGE PROBE")
    print("=" * 70)
    print(f"Query: {report.get('query', '')}")
    print(f"\nPREDICTION: {prediction}")
    print(f"REASONING:  {reasoning}")
    print(f"\nACTUAL:  {actual}")
    print(f"VERDICT: {verdict}")
    print(f"Rules: {total_fired}/{rules_evaluated_count(report)} fired")
    for rule in rules:
        marker = ">>>" if rule.get("fired") else "   "
        status = "FIRED" if rule.get("fired") else "not fired"
        print(f"  {marker} {rule.get('rule_name')} ({rule.get('rule_type')}): {status}")
    print(f"\nAnswer excerpt: {(report.get('answer') or '')[:150]}...")
    print("=" * 70)
    return verdict


def run_prediction_experiment(api, args: argparse.Namespace) -> None:
    total = 7

    print_section(1, total, "Creating vehicle inspection domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")

    print_section(2, total, "Uploading vehicle inspection data")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(3, total, "Building ontology")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=10)

    print_section(4, total, "Checking data quality")
    print_quality(api.datasets.quality(dataset["id"]))

    print_section(5, total, "Building platform")
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(6, total, "Running rule-coverage probes")
    results = []
    for query_text, prediction, reasoning in PREDICTION_QUERIES:
        report = api.platforms.query(platform["id"], query=query_text)
        verdict = evaluate_report(report, prediction, reasoning)
        results.append((query_text[:50], prediction, verdict))

    print_section(7, total, "Scorecard")
    correct = sum(1 for _, _, v in results if v == "CORRECT")
    wrong = sum(1 for _, _, v in results if v == "WRONG")
    observed = sum(1 for _, _, v in results if v == "OBSERVED")
    total_q = len(results)
    print(f"\n  Correct:  {correct}/{total_q}")
    print(f"  Wrong:    {wrong}/{total_q}")
    print(f"  Observed: {observed}/{total_q}")
    print(f"  Accuracy: {correct}/{total_q - observed} "
          f"({correct / max(total_q - observed, 1):.0%})")
    print()
    for desc, pred, verdict in results:
        icon = "+" if verdict == "CORRECT" else "-" if verdict == "WRONG" else "?"
        print(f"  [{icon}] {desc}... (predicted: {pred}, actual: {verdict})")

    print(f"\nDone. Platform {platform['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vehicle Inspection — AmberTrace AI rule-coverage experiment",
    )
    add_common_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: vehicle_inspections.csv)",
    )
    args = parser.parse_args()
    run_demo(run_prediction_experiment, args)


if __name__ == "__main__":
    main()
