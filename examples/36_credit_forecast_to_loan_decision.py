"""36 — Prediction → Decision: a credit-spread FORECAST feeding a verified lending DECISION.

The first example that wires an AmberTrace **Prediction** into an AmberTrace verified
**Query/Decision**. There is no single native call for this — forecasting and decisioning
are separate, independently-governed platforms — so the composition happens at the
APPLICATION layer, and the forecast enters the decision as a *certified fact*:

  1. FORECAST (Prediction platform). Build the credit-spread macro forecaster (same panel
     as ``33_credit_spread_macro_forecast.py``) and read ONE number: the one-month-ahead
     investment-grade credit spread (Moody's Baa − Aaa, %). This is CLASSICAL / SYMBOLIC
     forecasting — a gradient-boosted model over a macro panel plus an induced set of
     readable WHEN→THEN driver rules and a persistence baseline. It is not "neural AGI";
     the value is the explained fit, not a market-beating signal.
  2. DECIDE (verified Query/Decision platform). Build a verified lending platform whose
     classify-then-conclude policy references a ``forecast_credit_spread`` field alongside
     the applicant's own fields.
  3. BRIDGE. Pass the forecast value as one of the ``facts`` in ``platforms.query``. On the
     verified platform it is certified through the fact gate like any other ground fact, so
     the macro forecast becomes part of the machine-checked proof — not an opaque side input.

The showcase proves the forecast is *material*: a marginal borrower who APPROVES when the
forecast spread is benign is REFERRED to manual review when the forecast says credit
conditions are tightening — same applicant, different macro forecast, different auditable
outcome.

This is the SINGLE-forecast case; ``37_multi_forecast_policy_decision.py`` fans THREE
forecasts into one decision. Both are the ship-now, application-layer form of the
Prediction→Decision bridge — see the "Predictions → Decision bridge" section of the
examples README for the end-to-end pattern and the four gotchas each demo preserves.

DATA: the credit-spread panel is FRED (US-government public domain); the lending dataset
is a small SEEDED SYNTHETIC features-only table generated on first run (it only has to
DECLARE the schema — no labels). No FRED key is needed.

    python 36_credit_forecast_to_loan_decision.py                 # build the forecaster + decide
    python 36_credit_forecast_to_loan_decision.py --forecast-value 1.6  # force a regime (no build)
    python 36_credit_forecast_to_loan_decision.py --credit-platform-id 42  # reuse a forecaster
"""

from __future__ import annotations

import argparse
import csv
import random
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
    train_prediction_model,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
CREDIT_PANEL = DATA_DIR / "credit_macro_panel.csv"           # bundled (FRED, public domain)
LOAN_DATASET = DATA_DIR / "macro_aware_lending.csv"          # seeded on first run

# --- Prediction side (credit-spread forecaster) -----------------------------
CREDIT_TARGET = "IG_SPREAD"
CREDIT_DOMAIN_NAME = "US credit spread (system feature selection)"
CREDIT_DOMAIN_DESCRIPTION = (
    "Forecast IG_SPREAD, the US investment-grade credit spread (Moody's Baa minus Aaa corporate "
    "yield, in percent), one month ahead from a broad panel of US macro indicators: short rates "
    "(FEDFUNDS, GS2, GS1, TB3MS, GS10), inflation and prices (CPIAUCSL, CPILFESL, PPIACO, PCEPI), "
    "labour (UNRATE, PAYEMS, CIVPART), money and credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity "
    "(INDPRO, RSAFS, HOUST, PERMIT, TCU), consumer sentiment (UMCSENT) and the oil price "
    "(MCOILWTICO). Let the data decide which drivers matter for the credit risk premium."
)

# --- Decision side (lending policy that consumes the forecast) --------------
# The threshold that turns the macro forecast into a lending lever. IG_SPREAD runs
# ~0.5 (calm) to ~3.4 (stress); 1.20 sits above the ~0.93 long-run mean.
TIGHTENING_THRESHOLD = 1.20
LOAN_DOMAIN_NAME = "Macro-aware lending decision"
#
# GOTCHA 2 (stratification): the default outcome is NOT phrased "otherwise approve".
#   That gets induced as "approve if NOT (deny OR refer)", making the outcome depend on
#   the negation of ITSELF, and the verified build is rejected as non-stratifiable. Fix:
#   route each decision through intermediate CLASSIFICATION atoms (`blocked`, `needs manual
#   review`) and define each outcome over those, so negation is only ever over a
#   lower-stratum atom, never over the outcome.
#
# GOTCHA 3 (reachability): the intermediate atoms here use POSITIVE conditions only
#   ("applicant has weak credit", "credit conditions are tightening"). The FINAL outcome
#   layer may negate them ("approve when the application is not blocked and does not need
#   manual review") — that final-layer negation over already-derived intermediate atoms is
#   fine. It is negation INSIDE an intermediate atom that breaks reachability (see the
#   companion multi-forecast demo, where it bit and is called out explicitly).
LOAN_DOMAIN_DESCRIPTION = (
    "Lending decision support that is aware of the macro credit cycle. Each application has a "
    "credit score from 300 to 850, a debt-to-income ratio, a loan type (secured or unsecured), a "
    "requested loan amount, a collateral value (zero for unsecured loans), and a "
    "forecast_credit_spread: the one-month-ahead investment-grade credit spread "
    "(Moody's Baa minus Aaa, in percent) produced by the macro forecaster. "
    "Classify these named conditions: an applicant has strong credit when the credit score is at "
    "least 740; an applicant has weak credit when the credit score is below 660; an applicant "
    "is a marginal borrower when the credit score is at least 660 and below 740; debt-to-income "
    "is high when the debt-to-income ratio is above 0.40; a loan is well-secured when the loan "
    "type is secured and the loan amount is at most 80% of the collateral value; credit "
    "conditions are tightening when the forecast_credit_spread is at least 1.20. "
    "Also classify: the application is blocked when the applicant has weak credit and the loan "
    "is not well-secured, or when debt-to-income is high and the applicant does not have strong "
    "credit; the application needs manual review when credit conditions are tightening and the "
    "applicant is a marginal borrower. "
    "Decide the lending decision: deny when the application is blocked; refer when the "
    "application is not blocked and the application needs manual review; approve when the "
    "application is not blocked and the application does not need manual review. Every lending "
    "decision must be explainable and auditable for fair-lending compliance."
)

# Showcase applicants (without the macro fact — it is attached at query time).
# (label, expected_when_calm, expected_when_tightening, applicant_facts)
SHOWCASE = [
    ("marginal borrower (700), unsecured, clean DTI — the macro-sensitive case",
     "approve", "refer", {
         "credit_score": 700, "debt_to_income_ratio": 0.30, "loan_type": "unsecured",
         "loan_amount": 18000, "collateral_value": 0}),
    ("strong credit (780) — approves in any regime, forecast is not decisive",
     "approve", "approve", {
         "credit_score": 780, "debt_to_income_ratio": 0.35, "loan_type": "unsecured",
         "loan_amount": 25000, "collateral_value": 0}),
    ("weak credit (620), unsecured — denied on credit regardless of the macro forecast",
     "deny", "deny", {
         "credit_score": 620, "debt_to_income_ratio": 0.30, "loan_type": "unsecured",
         "loan_amount": 15000, "collateral_value": 0}),
    ("marginal borrower (690) but well-secured (LTV 0.40) — macro gate does not apply",
     "approve", "approve", {
         "credit_score": 690, "debt_to_income_ratio": 0.30, "loan_type": "secured",
         "loan_amount": 40000, "collateral_value": 100000}),
]


def _generate_loan_dataset(path: Path, n: int = 600) -> None:
    """Write a features-only lending dataset that DECLARES forecast_credit_spread.

    GOTCHA 1 (declared + in-domain certifying fact): the forecast field must be a DECLARED
    schema column in the decision domain, and the queried value must be IN-DOMAIN (within
    the column's observed range) or the verified fact gate rejects it. So the seeded dataset
    declares ``forecast_credit_spread`` spanning the historical IG_SPREAD range (~0.5–2.5)
    — any live or counterfactual forecast is in-domain — and the forecaster's live output is
    clamped into that range defensively before it is queried.
    """
    rng = random.Random(20260704)
    fields = ["credit_score", "debt_to_income_ratio", "loan_type",
              "loan_amount", "collateral_value", "forecast_credit_spread"]
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for _ in range(n):
            secured = rng.random() < 0.45
            loan_amount = rng.randint(5000, 100000)
            collateral = (rng.randint(loan_amount, loan_amount * 3) if secured else 0)
            w.writerow({
                "credit_score": rng.randint(580, 820),
                "debt_to_income_ratio": round(rng.uniform(0.10, 0.60), 2),
                "loan_type": "secured" if secured else "unsecured",
                "loan_amount": loan_amount,
                "collateral_value": collateral,
                "forecast_credit_spread": round(rng.uniform(0.50, 2.50), 2),
            })
    print(f"  generated {n} rows -> {path}")


def _forecast_credit_spread(api, args: argparse.Namespace) -> float:
    """The PREDICTION half: return the one-month-ahead IG_SPREAD LEVEL (a single number).

    GOTCHA 4 (read the LEVEL): read ``symbolic_forecast(...)["prediction_record"]["value"]``
    — the canonical Stage-A output, always LEVEL space and always present. Do NOT reach for a
    raw ``predict()`` value, which can be in change space on the no-history path.
    """
    lo, hi = 0.50, 2.50  # the declared in-domain range (GOTCHA 1)
    if args.forecast_value is not None:
        v = max(lo, min(hi, args.forecast_value))
        print(f"  using supplied forecast value: {v:.2f} (skipping the forecaster build)")
        return v

    if args.credit_platform_id:
        pid = args.credit_platform_id
        cfg = api.predictions.list_configs(pid)[0]
        print(f"  reusing credit forecast platform {pid}, config {cfg['id']}")
    else:
        if not CREDIT_PANEL.exists():
            print(f"ERROR: {CREDIT_PANEL} not found (should ship bundled).", file=sys.stderr)
            sys.exit(1)
        domain = api.domains.create(name=CREDIT_DOMAIN_NAME, description=CREDIT_DOMAIN_DESCRIPTION)
        dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(CREDIT_PANEL))
        print_dataset(dataset)
        build_ontology(api, domain["id"])
        platform = build_platform(
            api, domain["id"], dataset["id"],
            verified_profile=not args.standard, verified_min_confidence=args.tau)
        pid = platform["id"]
        # autoregressive="none": force the model to explain the spread through the macro
        # drivers rather than its own persistence. train() blocks and returns the settled
        # config (wait=True is the 1.0.0 default) — no hand-rolled poll needed.
        cfg = api.predictions.create_config(
            pid, mode="timeseries", target_field=CREDIT_TARGET, time_index_field="date",
            horizon=1, frequency="monthly", model_type="gbt", autoregressive="none")
        cfg = train_prediction_model(api, pid, cfg["id"])

    # symbolic_forecast returns the canonical, LEVEL-space prediction_record (1.0.0). Name it
    # + stamp an as_of so the record is addressable by a downstream Prediction→Decision fan-in.
    sf = api.predictions.symbolic_forecast(
        pid, prediction_config_id=cfg["id"], verified=not args.standard,
        prediction_name="ig_spread", as_of=args.as_of)
    record = sf.get("prediction_record") or {}
    raw = float(record.get("value"))
    clamped = max(lo, min(hi, raw))
    note = "" if clamped == raw else f"  (clamped from {raw:.2f} into [{lo}, {hi}])"
    proof = (record.get("proof_ref") or {}).get("proof_checked")
    print(f"  credit forecast platform {pid}: IG_SPREAD one-month-ahead forecast = "
          f"{raw:.3f}%{note}  (prediction proof_checked={proof}, "
          f"p={record.get('probability')})")
    return clamped


def _decide(api, pid: int, label: str, expected: str, facts: dict) -> str:
    try:
        report = api.platforms.query(pid, query="What is the lending decision?", facts=facts)
    except Exception as exc:  # a verified fail-safe refusal is an outcome, not a crash
        print(f"    VERIFIED FAIL-SAFE — refused to certify: {exc}")
        return "error"
    outcome = report.get("decision")
    mark = "OK" if outcome == expected else f"!! expected {expected}"
    print(f"    -> {str(outcome).upper():8s} [{mark}]  proof_checked={report.get('proof_checked')}")
    return outcome


def run_credit_to_loan(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "PREDICTION — forecast the credit spread (one number)")
    forecast = _forecast_credit_spread(api, args)
    regime = "TIGHTENING" if forecast >= TIGHTENING_THRESHOLD else "benign"
    print(f"  live regime: {regime} (threshold {TIGHTENING_THRESHOLD:.2f})")

    print_section(2, total, "Building the macro-aware lending domain (features only)")
    if not LOAN_DATASET.exists():
        _generate_loan_dataset(LOAN_DATASET)
    domain = api.domains.create(name=LOAN_DOMAIN_NAME, description=LOAN_DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(LOAN_DATASET))
    print_dataset(dataset)

    print_section(3, total, "Building verified lending platform (classify-then-conclude)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=14)
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    lpid = platform["id"]
    print(f"  Platform {lpid}: {platform['name']} ({platform.get('status')})")

    print_section(4, total, "DECISION — forecast enters each proof as a certified fact")
    # (a) Decide every showcase applicant under the LIVE forecast.
    print(f"\n  [LIVE forecast {forecast:.2f}% -> {regime}]")
    for label, exp_calm, exp_tight, facts in SHOWCASE:
        expected = exp_tight if forecast >= TIGHTENING_THRESHOLD else exp_calm
        print(f"  {label}")
        _decide(api, lpid, label, expected, {**facts, "forecast_credit_spread": forecast})

    # (b) Prove the forecast is MATERIAL: same marginal applicant, two macro regimes.
    print("\n  [COUNTERFACTUAL — same applicant, forecast flips the decision]")
    label, _, _, marginal = SHOWCASE[0]
    print(f"  {label}")
    for spread, exp in ((0.70, "approve"), (1.60, "refer")):
        band = "benign" if spread < TIGHTENING_THRESHOLD else "tightening"
        print(f"    forecast_credit_spread = {spread:.2f}  ({band})")
        _decide(api, lpid, label, exp, {**marginal, "forecast_credit_spread": spread})

    print(f"\nDone. Forecast platform -> value {forecast:.2f}% -> lending platform {lpid}. "
          "The macro forecast is a certified fact inside every lending proof.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prediction -> Decision: credit-spread forecast feeding a lending decision")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--forecast-value", type=float, default=None,
                        help="skip the forecaster build and use this IG_SPREAD value (%)")
    parser.add_argument("--credit-platform-id", type=int, default=None,
                        help="reuse an already-built credit forecast platform")
    parser.add_argument("--as-of", default=None,
                        help="alignment-key label stamped on the prediction record (e.g. 2026-06-30)")
    args = parser.parse_args()
    run_demo(run_credit_to_loan, args)


if __name__ == "__main__":
    main()
