"""41 — What-if preview of pending discovered rules (include_pending).

The 0.11.1 headline: a READ-ONLY "what-if" of accepted-but-PENDING discovered
correction rules, BEFORE the human approval gate. Discovery proposes correction
rules and stores them pending expert approval (is_active=False). Rather than
activate them blindly, you can score the neurosymbolic model AS IF those pending
rules were live — neurosymbolic_comparison(include_pending=True) applies them
read-only (is_active is NEVER mutated). See the lift first, then decide whether
to activate.

The six steps:
  1. Create the macro bond-yield domain + upload FRED data.
  2. Build the ontology + platform.
  3. Create a Time-Series prediction config (target=GS10) and train it.
  4. DISCOVER correction rules; print each accepted (pending) rule.
  5. Compare TWICE: (a) include_pending=False — baseline, active rules only
     (mode="active"); (b) include_pending=True — the what-if PREVIEW that layers
     the pending rules read-only (mode="preview_pending").
  6. OPTIONAL: if the discovered rules carry an id, ACTIVATE them via
     update_rule(is_active=True) and re-run the comparison — now the preview is
     reality. Otherwise note that activation needs the rule id from list_rules.

Dataset: data/fred_economic_data.csv (monthly, 2015 onwards). Columns: GS10
(10y Treasury yield, the target), FEDFUNDS, CPIAUCSL, DCOILWTICO (WTI oil),
UNRATE, M2SL.

Creates resources on your account. Needs a user-scoped key (at_...): discovery
is a WRITE operation. Run with --help for options.

    python 41_include_pending_whatif.py
    python 41_include_pending_whatif.py --max-rounds 2 -v
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from ambertraceai import AmbertraceError

from _common import (
    add_common_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "fred_economic_data.csv"

DOMAIN_NAME = "Pending-Rule What-If Forecasting"
DOMAIN_DESCRIPTION = (
    "Macroeconomic forecasting of the US 10-year Treasury yield (GS10). "
    "Each monthly observation includes the federal funds rate (FEDFUNDS), "
    "the consumer price index (CPIAUCSL), the WTI crude oil price "
    "(DCOILWTICO), the unemployment rate (UNRATE), and the M2 money supply "
    "(M2SL). The 10-year yield generally rises with the policy rate and "
    "inflation expectations and falls when growth weakens or investors seek "
    "safety. The goal is to forecast GS10 from these macro drivers and to learn "
    "transparent correction rules that adjust the forecast in known macro regimes."
)


def _fmt(value: Any, spec: str = ".4f") -> str:
    """Format a metric that may be None (too few rows to score)."""
    try:
        return format(float(value), spec)
    except (TypeError, ValueError):
        return "n/a"


def print_comparison(cmp: dict[str, Any]) -> None:
    neural = cmp.get("neural", {}) or {}
    nsai = cmp.get("neurosymbolic", {}) or {}
    delta = cmp.get("delta", {}) or {}
    print(f"  Target: {cmp.get('target', 'GS10')}   "
          f"correction rules: {cmp.get('n_adjustment_rules', 0)} adjustment / "
          f"{cmp.get('n_constraint_rules', 0)} constraint   "
          f"fire_rate={_fmt(cmp.get('fire_rate'), '.0%')}")
    print(f"\n    {'model':<16}{'R^2':>10}{'RMSE':>12}{'MAE':>12}{'n':>6}")
    print(f"    {'neural only':<16}{_fmt(neural.get('r2')):>10}"
          f"{_fmt(neural.get('rmse')):>12}{_fmt(neural.get('mae')):>12}"
          f"{str(neural.get('n', '?')):>6}")
    print(f"    {'neurosymbolic':<16}{_fmt(nsai.get('r2')):>10}"
          f"{_fmt(nsai.get('rmse')):>12}{_fmt(nsai.get('mae')):>12}"
          f"{str(nsai.get('n', '?')):>6}")
    print(f"\n  Delta (neurosymbolic − neural):  "
          f"R^2={_fmt(delta.get('r2'), '+.4f')}  RMSE={_fmt(delta.get('rmse'), '+.4f')}")
    d_r2 = delta.get("r2")
    if isinstance(d_r2, (int, float)):
        if d_r2 > 0:
            print("  => The symbolic correction layer IMPROVED accuracy — it earns its place.")
        elif d_r2 < 0:
            print("  => The symbolic layer did NOT help here — keep the neural model. "
                  "(The honest answer; the rules are still explainable.)")
        else:
            print("  => No measurable change from the symbolic layer.")


def print_accepted_rules(discovered: dict[str, Any]) -> list[dict]:
    rules = discovered.get("accepted_rules") or []
    print(f"  Accepted (pending) correction rules: "
          f"{discovered.get('total_accepted', len(rules))}")
    if not rules:
        print("  (No correction rule cleared the backtest — the neural model is "
              "already hard to beat on this data. That is the honest outcome.)")
        return rules
    for r in rules:
        print(f"\n    [{r.get('rule_type', '?')}] {r.get('name', '?')}")
        print(f"      fire_rate={_fmt(r.get('fire_rate'), '.0%')}  "
              f"delta={_fmt(r.get('delta'))}  is_active={r.get('is_active')}")
    return rules


def run_include_pending_demo(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Creating domain + uploading FRED macro data")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology + platform")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(3, total, "Creating prediction config (Time Series, target=GS10) + training")
    config = api.predictions.create_config(
        platform["id"],
        target_field="GS10",
        time_index_field="date",
        horizon=1,
        frequency="monthly",
        model_type="gbt",
    )
    print(f"  Config {config['id']}: target={config.get('target_field')}, "
          f"model={config.get('model_type')} ({config.get('status')})")
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Training complete: status={config.get('status')}")

    accepted_rules: list[dict] = []

    print_section(4, total, "Discovering correction rules (stored PENDING approval)")
    try:
        summary = api.predictions.discover_prediction_rules(
            platform["id"], prediction_config_id=config["id"],
            max_rounds=args.max_rounds, timeout=args.timeout,
        )
        print(f"  Discovery done: accepted={summary.get('total_accepted')}, "
              f"rejected={summary.get('total_rejected')}, "
              f"rounds={summary.get('rounds')}, converged={summary.get('converged')}")
        discovered = api.predictions.discovered_prediction_rules(
            platform["id"], prediction_config_id=config["id"],
        )
        accepted_rules = print_accepted_rules(discovered)
    except AmbertraceError as exc:
        print(f"  ! Rule discovery unavailable ({exc.status_code} {exc.code}): {exc}")

    print_section(5, total, "Comparison: baseline (active) vs what-if preview (pending)")
    try:
        print("\n  (a) BASELINE — active rules only (include_pending=False):")
        baseline = api.predictions.neurosymbolic_comparison(
            platform["id"], prediction_config_id=config["id"],
            include_pending=False, timeout=args.timeout,
        )
        print(f"      mode={baseline.get('mode')}")
        print_comparison(baseline)

        print("\n  (b) WHAT-IF PREVIEW — pending rules applied READ-ONLY "
              "(include_pending=True):")
        preview = api.predictions.neurosymbolic_comparison(
            platform["id"], prediction_config_id=config["id"],
            include_pending=True, timeout=args.timeout,
        )
        print(f"      mode={preview.get('mode')}  "
              f"n_pending_rules={preview.get('n_pending_rules')}")
        print_comparison(preview)
        print("\n  include_pending applies the accepted-but-pending rules read-only — "
              "is_active is NEVER mutated. This is the lift you would get IF you "
              "activated them, previewed before the human approval gate.")
    except AmbertraceError as exc:
        print(f"  ! Comparison unavailable ({exc.status_code} {exc.code}): {exc}")

    print_section(6, total, "Optional: activate the pending rules, then re-compare")
    rule_ids = [
        rid for r in accepted_rules
        if (rid := (r.get("id") or r.get("rule_id"))) is not None
    ]
    if not rule_ids:
        print("  No rule id on the discovered rules — to activate, fetch the id from "
              "api.platforms.list_rules(platform_id, include_inactive=True) and call "
              "update_rule(..., is_active=True). Skipping activation.")
    else:
        try:
            for rid in rule_ids:
                api.platforms.update_rule(platform["id"], rid, is_active=True)
            print(f"  Activated {len(rule_ids)} rule(s): {rule_ids} — the pending "
                  f"preview is now reality.")
            print("\n  Re-running comparison (include_pending=False) — the rules are "
                  "now ACTIVE:")
            after = api.predictions.neurosymbolic_comparison(
                platform["id"], prediction_config_id=config["id"],
                include_pending=False, timeout=args.timeout,
            )
            print(f"      mode={after.get('mode')}")
            print_comparison(after)
        except AmbertraceError as exc:
            print(f"  ! Activation/comparison unavailable ({exc.status_code} {exc.code}): {exc}")

    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="What-if preview of pending discovered rules (include_pending)",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument(
        "--max-rounds", type=int, default=None,
        help="Cap on discovery rounds (default: server decides).",
    )
    parser.add_argument(
        "--timeout", type=int, default=600,
        help="Seconds to wait for each async job (discovery / comparison).",
    )
    args = parser.parse_args()
    run_demo(run_include_pending_demo, args)


if __name__ == "__main__":
    main()
