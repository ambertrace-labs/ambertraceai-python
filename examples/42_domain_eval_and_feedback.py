"""42 — Domain Evaluation-Config & Feedback.

Walks the domain *evaluation-config* and *feedback* surface: the controls that
decide HOW a domain's answers are scored, plus the aggregated feedback the
platform collects on those answers.

An eval-config tells the platform how to evaluate (score / grade) the answers a
domain produces — which dimensions to score, thresholds, and the like. The
server can suggest a config for you; you then apply it, read it back, and check
feedback_stats, which aggregates the human feedback gathered on answers (counts,
agreement rates, and similar tallies).

Steps:
    1. Create a vehicle-inspection domain, upload the dataset, build the ontology.
    2. Ask the server to SUGGEST an eval-config (its own recommended shape).
    3. Apply it by round-tripping the suggestion straight back to set_eval_config.
    4. Read the active eval-config back.
    5. Fetch feedback_stats for the domain.

The set_eval_config body matches the ``EvalConfigUpdate`` model in
``ambertraceai/models`` — ``direction`` and ``target_metric`` are required; the
rest (``calculation`` / ``description`` / ``min_positive_fraction`` /
``significance_threshold_pp`` / ``unit``) are optional. We seed those fields from
the server's own suggestion when it provides them and fall back to sensible
defaults otherwise. The eval-config / feedback surface is a preview/admin
feature, so every write is still wrapped in ``try/except AmbertraceError`` and
reports cleanly if the endpoint is disabled.

Creates resources on your account. Run with --help for options.

    python 42_domain_eval_and_feedback.py
    python 42_domain_eval_and_feedback.py --dataset data/vehicle_inspections.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "vehicle_inspections.csv"

DOMAIN_NAME = "Vehicle Inspection Eval & Feedback"
DOMAIN_DESCRIPTION = (
    "Vehicle inspection pass/fail assessment covering MOT status, emissions, "
    "tyre tread, and brake efficiency. Used to demonstrate how a domain's "
    "answers are scored (eval-config) and how human feedback is aggregated."
)

# Keys a suggestion might nest its actual config payload under (it may also be a
# list of options, or carry the fields at the top level).
_CONFIG_KEYS = ("eval_config", "config", "suggested_config")

# The fields EvalConfigUpdate accepts (ambertraceai/models/eval_config_update.py).
# direction + target_metric are required; the rest are optional.
_EVAL_FIELDS = (
    "direction", "target_metric", "calculation", "description",
    "min_positive_fraction", "significance_threshold_pp", "unit",
)


def _report_error(label: str, exc: AmbertraceError) -> None:
    print(
        f"  {label} unavailable "
        f"(status={getattr(exc, 'status_code', '?')} "
        f"code={getattr(exc, 'code', '?')}): "
        f"{getattr(exc, 'message', None) or exc}"
    )


def _config_body(suggestion: Any) -> dict[str, Any]:
    """Build a valid EvalConfigUpdate body, seeded from the server's suggestion.

    Locates a config dict inside the suggestion (top-level fields, a known
    nested key, or the first option of a list), keeps only the fields
    EvalConfigUpdate accepts, and guarantees the two required fields
    (``direction`` / ``target_metric``) are present with sensible defaults.
    """
    candidate: dict[str, Any] = {}
    if isinstance(suggestion, dict):
        if any(k in suggestion for k in ("direction", "target_metric")):
            candidate = suggestion
        else:
            for key in (*_CONFIG_KEYS, "options", "suggestions"):
                inner = suggestion.get(key)
                if isinstance(inner, dict):
                    candidate = inner
                    break
                if isinstance(inner, list) and inner and isinstance(inner[0], dict):
                    candidate = inner[0]
                    break
    elif isinstance(suggestion, list) and suggestion and isinstance(suggestion[0], dict):
        candidate = suggestion[0]

    body = {k: candidate[k] for k in _EVAL_FIELDS if k in candidate}
    body.setdefault("direction", "maximize")
    body.setdefault("target_metric", "accuracy")
    return body


def run_eval_demo(api, args: argparse.Namespace) -> None:
    total = 5

    print_section(1, total, "Creating vehicle-inspection domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    domain_id = domain["id"]
    print(f"  Domain {domain_id}: {domain['name']} ({domain.get('status')})")

    dataset = api.datasets.upload(domain_id=domain_id, file_path=str(args.dataset))
    print_dataset(dataset)

    domain = build_ontology(api, domain_id)
    print_ontology(domain)

    print_section(2, total, "Suggesting an eval-config (server's recommended shape)")
    print(
        "  An eval-config defines HOW this domain's answers are scored "
        "(dimensions, thresholds).\n"
        "  We ask the server to suggest one — this is the authoritative shape "
        "to apply."
    )
    suggestion: Any = None
    try:
        suggestion = api.domains.suggest_eval_config(domain_id)
        print(f"  Suggested config: {suggestion}")
    except AmbertraceError as exc:
        _report_error("suggest_eval_config", exc)

    print_section(3, total, "Applying the eval-config (EvalConfigUpdate shape)")
    if suggestion is None:
        print("  No suggestion to apply — skipping set_eval_config.")
    else:
        body = _config_body(suggestion)
        try:
            result = api.domains.set_eval_config(domain_id, **body)
            print(f"  Applied. Server response: {result}")
        except AmbertraceError as exc:
            _report_error("set_eval_config", exc)
            print(f"  Attempted body: {body}")

    print_section(4, total, "Reading back the active eval-config")
    try:
        active = api.domains.eval_config(domain_id)
        print(f"  Active eval-config: {active}")
    except AmbertraceError as exc:
        _report_error("eval_config", exc)

    print_section(5, total, "Fetching feedback stats")
    print(
        "  feedback_stats aggregates the human feedback collected on this "
        "domain's answers\n"
        "  (e.g. counts of thumbs up/down, agreement rates)."
    )
    try:
        stats = api.domains.feedback_stats(domain_id)
        print(f"  Feedback stats: {stats}")
    except AmbertraceError as exc:
        _report_error("feedback_stats", exc)

    # Cleanup: remove the eval-config we applied (best-effort).
    try:
        api.domains.delete_eval_config(domain_id)
        print("\n  Cleanup: deleted eval-config.")
    except AmbertraceError as exc:
        _report_error("delete_eval_config (cleanup)", exc)

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Domain Evaluation-Config & Feedback — AmberTrace AI preview surface",
    )
    add_common_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: vehicle_inspections.csv)",
    )
    args = parser.parse_args()
    run_demo(run_eval_demo, args)


if __name__ == "__main__":
    main()
