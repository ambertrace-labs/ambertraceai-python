"""43 — Domain Rule Templates.

Walks the domain *rule-template* surface: reusable, parameterized rule scaffolds
attached to a domain. A template binds a condition field + operator and an action
field + type, with named params supplying the concrete values — so the scaffold
can be reused (with different params) when authoring rules across platforms.

Steps:
    1. Create a vehicle-inspection domain, upload the dataset, build the
       ontology, and build a (standard) platform.
    2. List existing templates (a safe GET).
    3. Create a template — an illustrative "flag a threshold breach" scaffold.
    4. If created, rename it and re-list to show the change.
    5. Clean up: delete the template we created.

The payload below matches the ``TemplateCreate`` model in
``ambertraceai/models`` (flat fields: ``name`` + ``template_id`` are required;
``condition_field`` / ``condition_operator`` / ``action_field`` / ``action_type``
/ ``name_template`` / ``param_to_*`` / ``params`` / ``category`` / ``is_active``
are optional). The rule-template surface is a preview/admin feature, so every
write is still wrapped in ``try/except AmbertraceError`` and reports cleanly if
the endpoint is disabled (404/403) on your account.

Creates resources on your account. Run with --help for options.

    python 43_domain_templates.py
    python 43_domain_templates.py --dataset data/vehicle_inspections.csv
"""

from __future__ import annotations

import argparse
from pathlib import Path

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "vehicle_inspections.csv"

DOMAIN_NAME = "Vehicle Inspection Rule Templates"
DOMAIN_DESCRIPTION = (
    "Vehicle inspection pass/fail assessment covering MOT status, emissions, "
    "tyre tread, and brake efficiency. Used to demonstrate reusable rule "
    "templates (scaffolds) attached to a domain."
)

# Template payload matching the TemplateCreate model (ambertraceai/models/
# template_create.py). A template is a PARAMETERIZED scaffold: it binds a
# condition field + operator and an action field + type, and the `params` map
# supplies the concrete values that `param_to_condition_value` /
# `param_to_action_value` point at. (The operator string is illustrative — the
# server validates it against its own operator vocabulary.)
TEMPLATE_PAYLOAD = {
    "name": "Threshold breach flag",
    "template_id": "threshold_breach_v1",          # required by TemplateCreate
    "category": "safety",
    "name_template": "Flag {condition_field} below {threshold}",
    "condition_field": "brake_efficiency_pct",
    "condition_operator": "lt",
    "param_to_condition_value": "threshold",
    "action_field": "inspection_result",
    "action_type": "classify",
    "param_to_action_value": "result",
    "is_active": True,
    "params": {"threshold": 58, "result": "fail"},
}


def _report_error(label: str, exc: AmbertraceError) -> None:
    print(
        f"  {label} unavailable "
        f"(status={getattr(exc, 'status_code', '?')} "
        f"code={getattr(exc, 'code', '?')}): "
        f"{getattr(exc, 'message', None) or exc}"
    )


def _print_templates(templates: object) -> None:
    items = templates if isinstance(templates, list) else []
    if not items:
        print("  (no templates)")
        return
    for tmpl in items:
        if isinstance(tmpl, dict):
            print(f"    Template {tmpl.get('id')}: {tmpl.get('name', '?')}")
        else:
            print(f"    Template: {tmpl}")


def run_template_demo(api, args: argparse.Namespace) -> None:
    total = 5

    print_section(1, total, "Creating vehicle-inspection domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    domain_id = domain["id"]
    print(f"  Domain {domain_id}: {domain['name']} ({domain.get('status')})")

    dataset = api.datasets.upload(domain_id=domain_id, file_path=str(args.dataset))
    print_dataset(dataset)

    domain = build_ontology(api, domain_id)
    print_ontology(domain)

    platform = build_platform(api, domain_id, dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(2, total, "Listing existing rule templates")
    try:
        _print_templates(api.domains.list_templates(domain_id))
    except AmbertraceError as exc:
        _report_error("list_templates", exc)

    print_section(3, total, "Creating a rule template (TemplateCreate shape)")
    template_id = None
    try:
        created = api.domains.create_template(domain_id, **TEMPLATE_PAYLOAD)
        template_id = created.get("id") if isinstance(created, dict) else None
        print(f"  Created template: {created}")
    except AmbertraceError as exc:
        _report_error("create_template", exc)
        print(f"  Attempted payload: {TEMPLATE_PAYLOAD}")

    print_section(4, total, "Updating the template and re-listing")
    if template_id is None:
        print("  No template was created — skipping update.")
    else:
        try:
            # TemplateUpdate fields are all optional; rename via `name`.
            updated = api.domains.update_template(
                domain_id, template_id,
                name="Threshold breach flag (revised)",
            )
            print(f"  Updated template: {updated}")
        except AmbertraceError as exc:
            _report_error("update_template", exc)
        try:
            _print_templates(api.domains.list_templates(domain_id))
        except AmbertraceError as exc:
            _report_error("list_templates", exc)

    print_section(5, total, "Cleaning up")
    if template_id is None:
        print("  Nothing to clean up.")
    else:
        try:
            api.domains.delete_template(domain_id, template_id)
            print(f"  Deleted template {template_id}.")
        except AmbertraceError as exc:
            _report_error("delete_template", exc)

    print("\nDone.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Domain Rule Templates — AmberTrace AI preview surface",
    )
    add_common_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: vehicle_inspections.csv)",
    )
    args = parser.parse_args()
    run_demo(run_template_demo, args)


if __name__ == "__main__":
    main()
