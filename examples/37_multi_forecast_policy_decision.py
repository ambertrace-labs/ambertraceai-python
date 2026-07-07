"""37 — Multiple Predictions → one Decision: three macro forecasts feeding a policy stance.

The multi-forecast companion to ``36_credit_forecast_to_loan_decision.py`` (a SINGLE
Prediction → Decision). It proves that ONE verified Query/Decision platform can consume
SEVERAL independent forecast platforms at once: ``facts`` has no arity limit, so each
forecaster's output is attached as its OWN certified fact and the policy rules combine them.

  1. FORECAST (three Prediction platforms). Build the inflation (INFL_YOY, monthly), real
     GDP growth (REAL_GDP_GROWTH, quarterly) and credit-spread (IG_SPREAD, monthly)
     forecasters — the same bundled panels as examples 32 / 34 / 33 — and read ONE number
     from each. Each is CLASSICAL / SYMBOLIC forecasting: a gradient-boosted model over a
     macro panel plus induced WHEN→THEN driver rules and a persistence baseline — explained
     fit, not a market-beating oracle.
  2. DECIDE (one verified Query/Decision platform). Build a "monetary policy stance" platform
     whose classify-then-conclude policy references all three forecast fields and concludes
     hike / hold / cut.
  3. BRIDGE. Fan all three forecasts into ONE machine-checked proof. Two paths (see below).

A nice teaching case: when inflation is hot but growth is too soft to be "strong", neither a
hike nor a cut is warranted → HOLD. The forecasts genuinely drive it.

TWO BRIDGE PATHS — prefer the NATIVE by-reference one
-----------------------------------------------------
* **NATIVE, fail-closed (recommended):** ``platforms.query(predictions={role:
  {"model_id": ..., "as_of": ...}, ...})`` — reference ALL THREE verified forecasts
  by role; the decision platform fetches each org-persisted, trusted record and
  folds its certified ``<role>.value`` into the ONE proof. The caller supplies no
  numbers. FAIL-CLOSED: if ANY referenced forecast is missing / uncertified /
  mis-aligned, its fact is absent and the decision abstains (fails closed over a
  partial fan-in). The decision domain must declare each fact as ``<role>.value``.
  See the ``query(predictions=...)`` docstring + the README bridge section.
* **MANUAL / application-layer (what THIS demo runs, for illustration):** read each
  ``prediction_record["value"]`` and pass all three as plain ``facts`` scalars —
  each certified through the fact gate, but the CALLER supplies the numbers. Use it
  for counterfactuals (the ``--*-value`` flags) or when the native path does not fit.

This demo exercises all four bridge gotchas; GOTCHA 3 (reachability) is the one it
specifically hit — see the ``POLICY_DOMAIN_DESCRIPTION`` comment. See the
"Predictions → Decision bridge" section of the examples README for both paths.

DATA: the three macro panels are FRED (US-government public domain, bundled); the policy
dataset is a small SEEDED SYNTHETIC features-only table generated on first run (labels-free —
it only has to DECLARE the three forecast fields). No FRED key is needed.

    python 37_multi_forecast_policy_decision.py
    python 37_multi_forecast_policy_decision.py --inflation-value 3.5 --gdp-value 2.8
    python 37_multi_forecast_policy_decision.py --credit-platform-id 42  # reuse a forecaster
"""

from __future__ import annotations

import argparse
import csv
import random
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
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
POLICY_DATASET = DATA_DIR / "policy_stance_inputs.csv"       # seeded on first run

# One spec per source forecaster: role key -> (target, panel CSV, frequency, decision fact
# field, in-domain range for the generated decision dataset / clamp bounds, forecast domain
# name + description). The three panels are the same bundled FRED panels examples 32/34/33 use.
FORECASTS = {
    "inflation": {
        "target": "INFL_YOY", "panel": "inflation_macro_panel.csv", "frequency": "monthly",
        "field": "forecast_inflation", "bounds": (-2.0, 9.0),
        "domain_name": "US inflation (system feature selection)",
        "domain_description": (
            "Forecast INFL_YOY, US headline CPI inflation year-over-year, one month ahead from a "
            "broad panel of US macro indicators: short rates and credit (FEDFUNDS, GS2, GS1, "
            "TB3MS, GS10, AAA, BAA), other price gauges (CPILFESL core CPI, PPIACO, PCEPI), labour "
            "(UNRATE, PAYEMS, CIVPART), money and credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity "
            "(INDPRO, RSAFS, HOUST, PERMIT, TCU), consumer sentiment (UMCSENT) and the oil price "
            "(MCOILWTICO). Let the data decide which drivers matter for inflation."),
    },
    "gdp": {
        "target": "REAL_GDP_GROWTH", "panel": "gdp_macro_panel.csv", "frequency": "quarterly",
        "field": "forecast_gdp_growth", "bounds": (-6.0, 8.0),
        "domain_name": "US real GDP growth (system feature selection)",
        "domain_description": (
            "Forecast REAL_GDP_GROWTH, US real GDP quarter-over-quarter annualised growth, one "
            "quarter ahead from a broad panel of US macro indicators observed at quarter-end: "
            "rates and credit (FEDFUNDS, GS2, GS1, TB3MS, GS10, AAA, BAA), inflation and prices "
            "(CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour (UNRATE, PAYEMS, CIVPART), money and "
            "credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), "
            "consumer sentiment (UMCSENT) and the oil price (MCOILWTICO). Let the data decide "
            "which drivers matter for real growth."),
    },
    "credit": {
        "target": "IG_SPREAD", "panel": "credit_macro_panel.csv", "frequency": "monthly",
        "field": "forecast_credit_spread", "bounds": (0.5, 3.4),
        "domain_name": "US credit spread (system feature selection)",
        "domain_description": (
            "Forecast IG_SPREAD, the US investment-grade credit spread (Moody's Baa minus Aaa "
            "corporate yield, in percent), one month ahead from a broad panel of US macro "
            "indicators: short rates (FEDFUNDS, GS2, GS1, TB3MS, GS10), inflation and prices "
            "(CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour (UNRATE, PAYEMS, CIVPART), money and "
            "credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), "
            "consumer sentiment (UMCSENT) and the oil price (MCOILWTICO). Let the data decide "
            "which drivers matter for the credit risk premium."),
    },
}
FORECAST_ORDER = ["inflation", "gdp", "credit"]

POLICY_DOMAIN_NAME = "Monetary policy stance"
#
# GOTCHA 2 (stratification): the stance is routed through intermediate `rate hike is
#   warranted` / `rate cut is warranted` atoms; the outcome never negates itself. A plain
#   "otherwise hold" phrasing gets induced as "hold if NOT (hike OR cut)" and the verified
#   build is REJECTED as non-stratifiable.
#
# GOTCHA 3 (reachability — the one THIS demo hit): the intermediate warrant atoms use
#   POSITIVE conditions only ("... and growth IS STRONG"). An earlier draft phrased tightening
#   as "inflation is hot and growth is NOT weak"; it built fine but the verified engine
#   ABSTAINED at query time — "a declared restrictive outcome has no reachable certifying path"
#   — because the negated intermediate never derived. NEGATION belongs only at the final stance
#   layer ("cut when a cut is warranted and a hike is NOT warranted"); keep it OUT of the
#   intermediate atoms. This is DISTINCT from GOTCHA 2: (2) is a build-time stratification
#   rejection over the OUTCOME; (3) is a query-time abstain from negation INSIDE an intermediate.
POLICY_DOMAIN_DESCRIPTION = (
    "Monetary policy stance decision from three macro forecasts: forecast_inflation (the "
    "year-over-year CPI inflation rate, in percent), forecast_gdp_growth (real GDP growth, "
    "annualized percent) and forecast_credit_spread (the investment-grade credit spread, Moody's "
    "Baa minus Aaa, in percent). "
    "Classify these named conditions: inflation is hot when forecast_inflation is at least 3.0; "
    "growth is strong when forecast_gdp_growth is at least 2.5; growth is weak when "
    "forecast_gdp_growth is at most 1.0; credit is stressed when forecast_credit_spread is at "
    "least 1.20. "
    "Also classify (using only positive conditions, so each has a reachable certifying path): a "
    "rate hike is warranted when inflation is hot and growth is strong; a rate cut is warranted "
    "when growth is weak; a rate cut is warranted when credit is stressed. "
    "Decide the policy stance: hike when a rate hike is warranted; cut when a rate cut is "
    "warranted and a rate hike is not warranted; hold when a rate hike is not warranted and a "
    "rate cut is not warranted. Every policy decision must be explainable and auditable."
)

# Showcase macro scenarios (label, expected stance, {fact field: forecast value}).
SHOWCASE = [
    ("overheating — inflation 3.5 (hot), growth 2.8 (strong), spread 0.7", "hike",
     {"forecast_inflation": 3.5, "forecast_gdp_growth": 2.8, "forecast_credit_spread": 0.7}),
    ("downturn — inflation 1.2, growth 0.5 (weak), spread 1.0", "cut",
     {"forecast_inflation": 1.2, "forecast_gdp_growth": 0.5, "forecast_credit_spread": 1.0}),
    ("credit stress — inflation 1.8, growth 2.0, spread 1.6 (stressed)", "cut",
     {"forecast_inflation": 1.8, "forecast_gdp_growth": 2.0, "forecast_credit_spread": 1.6}),
    ("goldilocks — inflation 2.0, growth 2.0, spread 0.8 (none fire)", "hold",
     {"forecast_inflation": 2.0, "forecast_gdp_growth": 2.0, "forecast_credit_spread": 0.8}),
]


def _generate_policy_dataset(path: Path, n: int = 480) -> None:
    """Features-only dataset that DECLARES the three forecast fields (spanning their ranges).

    GOTCHA 1 (declared + in-domain certifying fact): each forecast field must be a declared
    schema column and the queried value must be in-domain, or the verified fact gate rejects
    it. Each column here spans its forecaster's realistic range, and the live forecasts are
    clamped into the same range before they are queried.
    """
    rng = random.Random(20260704)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=[FORECASTS[k]["field"] for k in FORECAST_ORDER])
        w.writeheader()
        for _ in range(n):
            row = {}
            for key in FORECAST_ORDER:
                lo, hi = FORECASTS[key]["bounds"]
                row[FORECASTS[key]["field"]] = round(rng.uniform(lo, hi), 2)
            w.writerow(row)
    print(f"  generated {n} rows -> {path}")


def _forecast_one(api, args, key: str) -> float:
    """Build/reuse/override one forecaster; return its one-step-ahead LEVEL, clamped in-domain.

    GOTCHA 4 (read the LEVEL): read the canonical, always-present, always-LEVEL-space
    ``prediction_record["value"]`` from ``symbolic_forecast`` — not a raw ``predict()`` value
    that can be in change space on the no-history path.
    """
    spec = FORECASTS[key]
    lo, hi = spec["bounds"]
    override = getattr(args, f"{key}_value")
    if override is not None:
        print(f"  {key}: using supplied value {override:.2f} (no build)")
        return max(lo, min(hi, override))

    platform_id = getattr(args, f"{key}_platform_id")
    if platform_id:
        pid = platform_id
        cfg = api.predictions.list_configs(pid)[0]
        print(f"  {key}: reusing platform {pid}, config {cfg['id']}")
    else:
        panel = DATA_DIR / spec["panel"]
        domain = api.domains.create(name=spec["domain_name"],
                                    description=spec["domain_description"])
        dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(panel))
        build_ontology(api, domain["id"])
        platform = build_platform(
            api, domain["id"], dataset["id"],
            verified_profile=not args.standard, verified_min_confidence=args.tau)
        pid = platform["id"]
        # train() blocks + returns the settled config (1.0.0 wait=True default).
        cfg = api.predictions.create_config(
            pid, mode="timeseries", target_field=spec["target"], time_index_field="date",
            horizon=1, frequency=spec["frequency"], model_type="gbt", autoregressive="none")
        cfg = train_prediction_model(api, pid, cfg["id"])

    # The canonical Stage-A output: LEVEL-space prediction_record, named + as_of-stamped so it
    # is addressable by a Prediction->Decision fan-in.
    sf = api.predictions.symbolic_forecast(
        pid, prediction_config_id=cfg["id"], verified=not args.standard,
        prediction_name=key, as_of=args.as_of)
    record = sf.get("prediction_record") or {}
    raw = float(record.get("value"))
    clamped = max(lo, min(hi, raw))
    note = "" if clamped == raw else f"  (clamped from {raw:.2f} into [{lo}, {hi}])"
    proof = (record.get("proof_ref") or {}).get("proof_checked")
    print(f"  {key}: platform {pid} -> {spec['target']} forecast = {raw:.3f}{note} "
          f"(proof_checked={proof})")
    return clamped


def _decide(api, pid, facts, expected=None) -> str:
    # MANUAL bridge path (see the module docstring): the three forecast values are
    # passed as plain `facts` scalars the CALLER supplies. The NATIVE, fail-closed
    # path is `query(predictions={role: {"model_id": ..., "as_of": ...}, ...})`,
    # which references the platform-persisted verified forecasts by role so the
    # caller never supplies the numbers — prefer it when the decision domain
    # declares `<role>.value` fields.
    try:
        report = api.platforms.query(pid, query="What is the monetary policy stance?", facts=facts)
    except Exception as exc:  # a verified fail-safe refusal is an outcome, not a crash
        print(f"    VERIFIED FAIL-SAFE — refused to certify: {exc}")
        return "error"
    outcome = report.get("decision")
    if expected is None:
        tag = ""
    else:
        tag = " [OK]" if outcome == expected else f" [!! expected {expected}]"
    print(f"    -> {str(outcome).upper():5s}{tag}  proof_checked={report.get('proof_checked')}")
    return outcome


def run_multi_forecast_policy(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "PREDICTIONS — three macro forecasts (one number each)")
    live = {}
    for key in FORECAST_ORDER:
        live[FORECASTS[key]["field"]] = _forecast_one(api, args, key)

    print_section(2, total, "Building the policy-stance domain (3 forecast fields)")
    if not POLICY_DATASET.exists():
        _generate_policy_dataset(POLICY_DATASET)
    domain = api.domains.create(name=POLICY_DOMAIN_NAME, description=POLICY_DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(POLICY_DATASET))
    print_dataset(dataset)

    print_section(3, total, "Building verified policy platform (classify-then-conclude)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=16)
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    ppid = platform["id"]
    print(f"  Platform {ppid}: {platform['name']} ({platform.get('status')})")

    print_section(4, total, "DECISION — three forecasts as certified facts in one proof")
    live_str = ", ".join(f"{k.split('_', 1)[1]}={v:.2f}" for k, v in live.items())
    print(f"\n  [LIVE forecasts: {live_str}]")
    _decide(api, ppid, live)

    print("\n  [SCENARIOS — the same platform, different macro forecasts]")
    for label, expected, facts in SHOWCASE:
        print(f"  {label}")
        _decide(api, ppid, facts, expected)

    print(f"\nDone. 3 forecast platforms -> policy platform {ppid}. "
          "Each macro forecast is a certified fact inside the one policy proof.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Multiple Predictions -> one Decision: macro forecasts -> policy stance")
    add_common_args(parser)
    add_verified_args(parser)
    for key in FORECAST_ORDER:
        parser.add_argument(f"--{key}-value", type=float, default=None,
                            help=f"skip the {key} forecaster build and use this value")
        parser.add_argument(f"--{key}-platform-id", type=int, default=None,
                            help=f"reuse an already-built {key} forecast platform")
    parser.add_argument("--as-of", default=None,
                        help="alignment-key label stamped on each prediction record (e.g. 2026-06-30)")
    args = parser.parse_args()
    run_demo(run_multi_forecast_policy, args)


if __name__ == "__main__":
    main()
