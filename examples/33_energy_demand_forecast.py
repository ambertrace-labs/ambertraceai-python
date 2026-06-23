"""33 — Neurosymbolic daily electricity demand forecast (the full flow).

A self-contained forecasting walkthrough that needs no external connector — it
uploads a local CSV of daily electricity demand and weather covariates, then runs
the *neurosymbolic* loop end to end: train a neural model, DISCOVER explainable
correction rules from its residuals, read a transparent symbolic forecast with its
WHY, and finally put the neural-only and neurosymbolic models head to head so you
can see — honestly — whether the symbolic layer earns its place.

The six steps:
  1. Create the domain (describing the demand drivers + weather regimes in plain
     English) and upload the local daily demand CSV. No connector step.
  2. Build the ontology + platform (symbolic rules over weather regimes).
  3. Create a Time-Series prediction config (target = demand_mwh).
  4. Train the model, then DISCOVER correction rules and print each accepted
     rule with its fire-rate and backtest delta.
  5. Run the symbolic forecast (``include_fitted_series=True``) and print the
     driver-rules (WHY) behind the number.
  6. Compare neural vs neurosymbolic R² / RMSE — the "does the symbolic layer
     earn its place?" moment.

Dataset: data/energy_demand.csv (~150 daily rows). Columns: demand_mwh
(electricity demand in MWh, the target), temperature_f, heating_degree_days,
cooling_degree_days, is_weekend. Demand rises with heating and cooling degree
days and dips on weekends, so the discovery step has structure to find.

Creates resources on your account. Needs a user-scoped key (at_...): discovery
is a WRITE operation. Run with --help for options.

    python 33_energy_demand_forecast.py
    python 33_energy_demand_forecast.py --max-rounds 2 -v
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
DEFAULT_DATASET = DATA_DIR / "energy_demand.csv"

DOMAIN_NAME = "Neurosymbolic Energy Demand Forecasting"
DOMAIN_DESCRIPTION = (
    "Daily electricity demand forecasting for an electric utility. Each daily "
    "observation includes the average temperature (temperature_f), the heating "
    "degree days (heating_degree_days = max(0, 65 - avg temp)), the cooling "
    "degree days (cooling_degree_days = max(0, avg temp - 65)), and a weekend "
    "flag (is_weekend). Electricity demand (demand_mwh) rises in the cold regime "
    "as heating degree days climb and in the hot regime as cooling degree days "
    "climb, and it dips on weekends when commercial and industrial load is low. "
    "The goal is to forecast demand_mwh from these weather drivers and to learn "
    "transparent correction rules that adjust the forecast in known weather and "
    "calendar regimes."
)

FEATURE_FIELDS = [
    "temperature_f",
    "heating_degree_days",
    "cooling_degree_days",
    "is_weekend",
]


def _fmt(value: Any, spec: str = ".4f") -> str:
    """Format a metric that may be None (too few rows to score)."""
    try:
        return format(float(value), spec)
    except (TypeError, ValueError):
        return "n/a"


def print_discovered_rules(discovered: dict[str, Any]) -> None:
    rules = discovered.get("accepted_rules") or []
    print(f"  Accepted correction rules: {discovered.get('total_accepted', len(rules))}")
    if not rules:
        print("  (No correction rule cleared the backtest — the neural model is "
              "already hard to beat on this data. That is the honest outcome.)")
        return
    for r in rules:
        delta = r.get("delta")
        delta_str = _fmt(delta) if delta is not None else "n/a"
        print(f"\n    [{r.get('rule_type', '?')}] {r.get('name', '?')}")
        if r.get("description"):
            print(f"      {r['description']}")
        print(f"      fire_rate={_fmt(r.get('fire_rate'), '.0%')}  "
              f"backtest delta ({r.get('eval_metric', 'metric')})={delta_str}  "
              f"round={r.get('discovery_round', '?')}  active={r.get('is_active')}")
    print("\n  Discovered rules are stored PENDING EXPERT APPROVAL (is_active=False). "
          "Review them, then activate with api.platforms.update_rule(...).")


def print_why(forecast: dict[str, Any]) -> None:
    fc = forecast.get("forecast", {}) or {}
    print(f"  Forecast demand_mwh: {_fmt(fc.get('value'), '.2f')} MWh  "
          f"[{_fmt(fc.get('lower'), '.2f')}, {_fmt(fc.get('upper'), '.2f')}]")
    print(f"  Baseline (persistence): {_fmt(forecast.get('baseline'), '.2f')} MWh   "
          f"skill_vs_persistence={_fmt(forecast.get('skill_vs_persistence'))}")

    why = forecast.get("why") or []
    n_active = sum(1 for w in why if w.get("fired_on_latest_row"))
    print(f"\n  WHY — {len(why)} driver-rule(s) ({n_active} active on the latest row):")
    for w in why:
        active = "active-now" if w.get("fired_on_latest_row") else "latent"
        named = ", ".join(w.get("base_features") or []) or "—"
        print(f"    - {w.get('driver', '?')}")
        print(f"        direction={w.get('direction')}  "
              f"contribution={_fmt(w.get('contribution'), '.4f')}  "
              f"drivers={named}  ({active})")

    series = (forecast.get("fitted_series") or {}).get("series") or []
    if series:
        print(f"\n  Fitted-vs-actual backtest: {len(series)} out-of-sample points "
              f"({forecast['fitted_series'].get('basis')}).")
        last = series[-1]
        print(f"    Most recent point: actual={_fmt(last.get('actual'), '.2f')}  "
              f"predicted={_fmt(last.get('predicted'), '.2f')}  "
              f"persistence={_fmt(last.get('persistence'), '.2f')}")


def print_comparison(cmp: dict[str, Any]) -> None:
    neural = cmp.get("neural", {}) or {}
    nsai = cmp.get("neurosymbolic", {}) or {}
    delta = cmp.get("delta", {}) or {}
    print(f"  Target: {cmp.get('target', 'demand_mwh')}   "
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


def run_energy_demand_forecast(api, args: argparse.Namespace) -> None:
    total = 6

    print_section(1, total, "Creating domain + uploading daily demand CSV")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    print("  Uploading local energy demand CSV (no connector needed)")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology + platform")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(3, total, "Creating prediction config (Time Series, target=demand_mwh)")
    config = api.predictions.create_config(
        platform["id"],
        target_field="demand_mwh",
        time_index_field="date",
        horizon=1,
        frequency="daily",
        model_type="gbt",
        feature_fields=FEATURE_FIELDS,
    )
    print(f"  Config {config['id']}: target={config.get('target_field')}, "
          f"model={config.get('model_type')} ({config.get('status')})")

    print_section(4, total, "Training, then discovering correction rules")
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Training complete: status={config.get('status')}")
    print("  Discovering correction rules (this runs a background A/B backtest)...")
    try:
        summary = api.predictions.discover_prediction_rules(
            platform["id"], prediction_config_id=config["id"],
            max_rounds=args.max_rounds, timeout=args.timeout,
        )
        print(f"  Discovery done: accepted={summary.get('total_accepted')}, "
              f"rejected={summary.get('total_rejected')}, "
              f"rounds={summary.get('rounds')}, converged={summary.get('converged')} "
              f"({summary.get('convergence_reason')})")
        discovered = api.predictions.discovered_prediction_rules(
            platform["id"], prediction_config_id=config["id"],
        )
        print_discovered_rules(discovered)
    except AmbertraceError as exc:
        print(f"  ! Rule discovery unavailable ({exc.status_code} {exc.code}): {exc}")

    print_section(5, total, "Symbolic forecast + WHY")
    try:
        forecast = api.predictions.symbolic_forecast(
            platform["id"], prediction_config_id=config["id"],
            include_fitted_series=True,
        )
        print_why(forecast)
    except AmbertraceError as exc:
        print(f"  ! Symbolic forecast unavailable ({exc.status_code} {exc.code}): {exc}")
        if exc.status_code == 404:
            print("    (The symbolic-forecast preview feature may be disabled here.)")

    print_section(6, total, "Neural vs neurosymbolic comparison")
    try:
        comparison = api.predictions.neurosymbolic_comparison(
            platform["id"], prediction_config_id=config["id"], timeout=args.timeout,
        )
        print_comparison(comparison)
    except AmbertraceError as exc:
        print(f"  ! Comparison unavailable ({exc.status_code} {exc.code}): {exc}")

    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Neurosymbolic daily electricity demand forecast — the full flow",
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
    run_demo(run_energy_demand_forecast, args)


if __name__ == "__main__":
    main()
