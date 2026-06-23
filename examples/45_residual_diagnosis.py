"""45 — Residual diagnosis: is a forecast miss DRIFT or CORRECTION?

When a forecast misses, the question that matters is *why*. Ambertrace's
residual diagnosis takes a forecast value and the realised actual, standardises
the residual, and — when the miss breaches the gate ``|z| > k`` — attributes it
to the driver-rules behind the number:
  - a decayed driver that pointed away from the realised move  => **drift**
    (the model is going stale; the residual is likely to keep widening), versus
  - the still-reliable drivers pointing counter to the move     => **correction**
    (the target dislocated; the residual is likely to tighten).

The five steps:
  1. Create the macro domain + upload FRED data + build ontology + platform.
  2. Create a Time-Series prediction config (target = GS10) and train it.
  3. Read a forecast value (symbolic forecast, falling back to predict()).
  4. Diagnose a SMALL miss (actual within noise) — expect breached=False.
  5. Diagnose a LARGE miss — expect breached=True with a drift/correction verdict
     plus its decayed/stable drivers and supporting evidence.

Dataset: data/fred_economic_data.csv (monthly, 2015 onwards). Target: GS10
(the US 10-year Treasury yield).

NOTE: residual diagnosis and the symbolic forecast are PREVIEW features and may
return 404 on deployments where they are disabled; the calls are wrapped so the
demo reports that cleanly.

Creates resources on your account (a domain, dataset, platform, and prediction
config). Run with --help for options.

    python 45_residual_diagnosis.py
    python 45_residual_diagnosis.py --dataset data/fred_economic_data.csv -v
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
    prediction_values,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "fred_economic_data.csv"

DOMAIN_NAME = "Residual Diagnosis — Macro Forecasting"
DOMAIN_DESCRIPTION = (
    "Macroeconomic forecasting of the US 10-year Treasury yield (GS10) from "
    "monthly macro drivers: the federal funds rate (FEDFUNDS), the consumer "
    "price index (CPIAUCSL), the WTI crude oil price (DCOILWTICO), the "
    "unemployment rate (UNRATE), and the M2 money supply (M2SL). The goal is to "
    "forecast GS10 and to diagnose forecast misses as drift versus correction."
)


def _fmt(value: Any, spec: str = ".4f") -> str:
    """Format a metric that may be None (too few rows to score)."""
    try:
        return format(float(value), spec)
    except (TypeError, ValueError):
        return "n/a"


def _print_diagnosis(label: str, diag: dict[str, Any], *, full: bool) -> None:
    print(f"\n  {label}")
    print(f"    residual={_fmt(diag.get('residual'), '.4f')}  "
          f"z={_fmt(diag.get('z'), '.2f')}  "
          f"breached={diag.get('breached')}  "
          f"diagnosis={diag.get('diagnosis')}")
    if not full:
        return
    decayed = diag.get("decayed_drivers") or []
    stable = diag.get("stable_drivers") or []
    print(f"    decayed_drivers: {decayed or '—'}")
    print(f"    stable_drivers:  {stable or '—'}")
    evidence = diag.get("evidence")
    if evidence:
        print(f"    evidence: {evidence}")


def run_residual_diagnosis(api, args: argparse.Namespace) -> None:
    total = 5

    print_section(1, total, "Creating domain + loading data, ontology, platform")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    print(f"  Domain {domain['id']}: {domain['name']} ({domain.get('status')})")
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)
    domain = build_ontology(api, domain["id"])
    print_ontology(domain)
    platform = build_platform(api, domain["id"], dataset["id"])
    print(f"  Platform {platform['id']}: {platform['name']} ({platform.get('status')})")

    print_section(2, total, "Creating + training prediction config (target=GS10)")
    config = api.predictions.create_config(
        platform["id"],
        target_field="GS10",
        time_index_field="date",
        horizon=1,
        frequency="monthly",
        model_type="gbt",
    )
    config = train_prediction_model(api, platform["id"], config["id"])
    print(f"  Config {config['id']}: target={config.get('target_field')}, "
          f"status={config.get('status')}")

    print_section(3, total, "Reading a forecast value")
    value: float | None = None
    try:
        forecast = api.predictions.symbolic_forecast(
            platform["id"], prediction_config_id=config["id"],
            include_fitted_series=False,
        )
        value = float((forecast.get("forecast") or {}).get("value"))
        print(f"  Symbolic forecast GS10: {_fmt(value, '.4f')}")
    except (AmbertraceError, TypeError, ValueError) as exc:
        print(f"  Symbolic forecast unavailable ({exc}) — falling back to predict()")
        try:
            prediction = api.predictions.predict(
                platform["id"], prediction_config_id=config["id"],
            )
            value, _lower, _upper = prediction_values(prediction)
            print(f"  Forecast GS10 (predict): {_fmt(value, '.4f')}")
        except AmbertraceError as exc2:
            print(f"  ! Could not obtain a forecast value ({exc2.status_code} "
                  f"{exc2.code}): {exc2}")
            print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")
            return

    # A small miss sits within noise; a large miss should breach the gate.
    small_actual = value + 0.02
    large_actual = value + max(1.5, abs(value) * 0.5)

    print_section(4, total, "Diagnosing a SMALL miss (within noise) — expect breached=False")
    try:
        diag = api.predictions.residual_diagnosis(
            platform["id"], prediction_config_id=config["id"],
            value=value, actual=small_actual,
        )
        print(f"  value={_fmt(value, '.4f')}  actual={_fmt(small_actual, '.4f')}")
        _print_diagnosis("Small-miss diagnosis:", diag, full=False)
    except AmbertraceError as exc:
        print(f"  ! Residual diagnosis unavailable ({exc.status_code} {exc.code}): {exc}")
        if exc.status_code == 404:
            print("    (The residual-diagnosis preview feature may be disabled here.)")

    print_section(5, total, "Diagnosing a LARGE miss — expect breached=True (drift|correction)")
    try:
        diag = api.predictions.residual_diagnosis(
            platform["id"], prediction_config_id=config["id"],
            value=value, actual=large_actual,
        )
        print(f"  value={_fmt(value, '.4f')}  actual={_fmt(large_actual, '.4f')}")
        _print_diagnosis("Large-miss diagnosis:", diag, full=True)
    except AmbertraceError as exc:
        print(f"  ! Residual diagnosis unavailable ({exc.status_code} {exc.code}): {exc}")
        if exc.status_code == 404:
            print("    (The residual-diagnosis preview feature may be disabled here.)")

    print(f"\nDone. Platform {platform['id']}, PredictionConfig {config['id']}.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Residual diagnosis — drift vs correction on a forecast miss",
    )
    add_common_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    args = parser.parse_args()
    run_demo(run_residual_diagnosis, args)


if __name__ == "__main__":
    main()
