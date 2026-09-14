"""48 — A forecast with NO last-value anchor (``autoregressive="none"`` + ``target_transform="none"``).

"Don't just tell me last month's number." Two knobs control how much of a
forecast is really the previous observation, and **you need BOTH** — this is the
trap this demo exists to close:

1. ``autoregressive="none"`` (a TOP-LEVEL ``create_config`` kwarg) removes the
   TARGET's own engineered features (its lags, rate-of-change, rolling mean/std),
   so the model must explain the target through your other indicators.
2. ``feature_config={"target_transform": "none"}`` (NESTED inside
   ``feature_config``) makes the model forecast the raw LEVEL ``y_{t+h}``
   directly, so the forecast is **not** reconstructed as ``last_value + Δ̂``.
   The equivalent TOP-LEVEL shorthand ``target_transform="none"`` works too —
   both forms are accepted and mean exactly the same thing (step 5 below
   demonstrates the shorthand and asserts the echoed output space).

``autoregressive="none"`` ALONE does not remove the last-value anchor.
``target_transform`` defaults to ``"auto"``, which for a trending or
random-walk-ish series resolves to ``"difference"`` — the model then predicts the
CHANGE and the returned level is ``baseline + change``, i.e. still anchored on the
last observation. The knob that removes the anchor is ``target_transform="none"``.

This demo trains TWO configs on ONE platform over the same bundled panel and
prints the contrast, reading it off the config echo (no guessing):

  * ``resolved_target_transform`` — the transform actually applied;
  * ``output_space`` — ``"change"`` (anchored, reconstructed) vs ``"level"``
    (modelled directly);
  * ``target_transform_reason`` — ``"explicit"`` when you chose, or the
    auto-heuristic's reason;
  * ``prediction.baseline`` — the level a differenced forecast was rebuilt from
    (``null`` on the level-direct config: there is nothing to rebuild from).

**``skill_vs_persistence`` is still reported.** It is computed from the ground
truth in the backtest window (``y_true[t] - y_true[t-1]``), so persistence stays
the BENCHMARK even when it is no longer a COMPONENT of the model. The demo
asserts it is populated on the level-direct config.

**The honest caveat.** A tree model cannot extrapolate beyond the target range it
saw in training. On a strongly TRENDING target, ``target_transform="none"``
therefore tends to saturate and can post a sharply NEGATIVE R² — which is exactly
why ``"auto"`` differences a trending target for you. Use ``"none"`` when you need
a genuinely persistence-free forecast (or when the target is mean-reverting, like
the credit spread used here), and read the level metrics before trusting it.

DATA: all FRED, US-government public domain — the panel is bundled and fully
reproducible; no API key is needed to run this demo.

    python 48_no_ar_level_direct_forecast.py             # both configs, contrast
    python 48_no_ar_level_direct_forecast.py --standard  # skip the verified profile
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    build_platform,
    print_dataset,
    print_section,
    run_demo,
    train_prediction_model,
)
from ambertraceai import AmbertraceError

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "credit_macro_panel.csv"
TARGET = "IG_SPREAD"

DOMAIN_NAME = "Credit spread — persistence-free forecast"
DOMAIN_DESCRIPTION = (
    "Forecast IG_SPREAD, the US investment-grade credit spread (Moody's Baa minus Aaa "
    "corporate yield, in percent), one month ahead from a broad panel of US macro "
    "indicators: short rates (FEDFUNDS, GS2, GS1, TB3MS, GS10), inflation and prices "
    "(CPIAUCSL, CPILFESL, PPIACO, PCEPI), labour (UNRATE, PAYEMS, CIVPART), money and "
    "credit (M2SL, M1SL, TOTALSL, BUSLOANS), activity (INDPRO, RSAFS, HOUST, PERMIT, TCU), "
    "consumer sentiment (UMCSENT) and the oil price (MCOILWTICO). The forecast must come "
    "from the drivers, not from the spread's own last value."
)


def _config_space(cfg: dict[str, Any]) -> str:
    """The forecast space a config declares BEFORE you predict (the config echo)."""
    return (
        f"resolved_target_transform={cfg.get('resolved_target_transform')!r} "
        f"output_space={cfg.get('output_space')!r} "
        f"reason={cfg.get('target_transform_reason')!r}"
    )


def _metrics(prediction: dict[str, Any]) -> dict[str, Any]:
    model = (prediction.get("explanation") or {}).get("model") or {}
    metrics = model.get("metrics") or {}
    return {
        "level": metrics.get("level") or {},
        "transformed": metrics.get("transformed") or {},
        "skill": metrics.get("skill_vs_persistence", model.get("skill_vs_persistence")),
    }


def _print_forecast(label: str, cfg: dict[str, Any], prediction: dict[str, Any]) -> None:
    pred = prediction.get("prediction") or {}
    m = _metrics(prediction)
    print(f"  [{label}] {_config_space(cfg)}")
    print(f"    value={pred.get('value')}  value_change={pred.get('value_change')}  "
          f"value_space={pred.get('value_space')!r}")
    print(f"    baseline={pred.get('baseline')}  "
          "<- the last-value anchor (None => no anchor)")
    print(f"    fit (level): R^2={m['level'].get('r2')} RMSE={m['level'].get('rmse')}")
    if isinstance(m["skill"], (int, float)):
        print(f"    skill_vs_persistence={m['skill']:+.3f} — persistence is still the "
              "BENCHMARK, computed from the ground truth, not from the model.")


def run_no_ar_level_direct(api, args: argparse.Namespace) -> None:
    if not args.dataset.exists():
        print(f"ERROR: {args.dataset} not found.", file=sys.stderr)
        sys.exit(1)
    total = 5

    print_section(1, total, "Creating domain + uploading the bundled credit-spread panel")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology + platform")
    build_ontology(api, domain["id"])
    platform = build_platform(
        api, domain["id"], dataset["id"],
        verified_profile=not args.standard, verified_min_confidence=args.tau)
    pid = platform["id"]

    common = dict(mode="timeseries", target_field=TARGET, time_index_field="date",
                  horizon=args.horizon, frequency="monthly", model_type="gbt",
                  autoregressive="none")

    print_section(3, total, "THE TRAP — autoregressive='none' alone still anchors on last value")
    # target_transform='auto' is the DEFAULT (what you get by omitting it). On a
    # trending / random-walk-ish target auto resolves to 'difference', so the
    # returned level is baseline + change: the last observation is STILL in the
    # forecast even with no AR features. 'auto' resolves at TRAIN time, so the
    # config echo reads "auto (resolved at train time)" until it is trained.
    anchored = api.predictions.create_config(
        pid, **common, feature_config={"target_transform": "auto"})
    print(f"  config {anchored['id']} (target_transform='auto', the default): "
          f"{_config_space(anchored)}")
    anchored = train_prediction_model(api, pid, anchored["id"])
    anchored_pred = api.predictions.predict(pid, prediction_config_id=anchored["id"])
    _print_forecast("auto", anchored, anchored_pred)

    print_section(4, total, "THE RECIPE — no AR features AND no last-value anchor")
    # BOTH knobs: autoregressive='none' (top level) + target_transform='none'
    # (nested in feature_config). The model forecasts the raw level y_{t+h}, so
    # there is no `last_value + delta` reconstruction step at all.
    direct = api.predictions.create_config(
        pid, **common, feature_config={"target_transform": "none"})
    print(f"  config {direct['id']} (feature_config={{'target_transform': 'none'}}): "
          f"{_config_space(direct)}")
    # An EXPLICIT transform is echoed on the config immediately — you know the
    # output space before training, let alone predicting.
    assert direct.get("resolved_target_transform") == "none", direct
    assert direct.get("output_space") == "level", direct

    direct = train_prediction_model(api, pid, direct["id"])
    # target_transform_reason is populated once trained: 'explicit' because you
    # chose the transform rather than letting the auto-heuristic decide.
    assert direct.get("target_transform_reason") == "explicit", direct
    direct_pred = api.predictions.predict(pid, prediction_config_id=direct["id"])
    _print_forecast("level-direct", direct, direct_pred)

    print_section(5, total, "THE SHORTHAND — target_transform as a top-level kwarg")
    # Both forms are accepted and mean the same thing: the TOP-LEVEL
    # target_transform="difference" kwarg is folded into feature_config for you.
    # This step asserts the config echoes the transform back, so you can confirm
    # it was applied.
    shorthand = api.predictions.create_config(
        pid, **common, target_transform="difference")
    print(f"  config {shorthand['id']} (target_transform='difference', top level): "
          f"{_config_space(shorthand)}")
    assert shorthand.get("resolved_target_transform") == "difference", shorthand
    assert shorthand.get("output_space") == "change", shorthand
    # An unknown value is REJECTED (422) rather than silently resolving to 'none'.
    try:
        api.predictions.create_config(pid, **common, target_transform="bogus_value_xyz")
    except AmbertraceError as exc:
        print(f"  bogus target_transform rejected as expected: {exc}")
    else:  # pragma: no cover - the server must reject this
        raise AssertionError("a bogus target_transform must be rejected with 422")

    direct_metrics = _metrics(direct_pred)
    # The point of the demo: no anchor, yet the skill metric is still there.
    assert (direct_pred.get("prediction") or {}).get("baseline") is None, direct_pred
    assert isinstance(direct_metrics["skill"], (int, float)), (
        "skill_vs_persistence must still be reported for a level-direct model — "
        f"got {direct_metrics['skill']!r}")

    level_r2 = direct_metrics["level"].get("r2")
    print(f"\nDone. Platform {pid}. Config {direct['id']} is persistence-free: no "
          "target-history features and no last-value reconstruction, and "
          f"skill_vs_persistence={direct_metrics['skill']:+.3f} still measures it "
          "against 'predict the last value'.")
    if isinstance(level_r2, (int, float)) and level_r2 < 0:
        print("  NOTE: level R^2 is negative — a level-direct tree cannot extrapolate "
              "beyond its training range, so on a TRENDING target this is the expected "
              "cost of removing the anchor. Use target_transform='auto'/'difference' "
              "when you want the trend handled for you.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Persistence-free forecast — no AR features, no last-value anchor")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET,
                        help="bundled macro panel CSV")
    parser.add_argument("--horizon", type=int, default=1, help="forecast horizon in months")
    args = parser.parse_args()
    run_demo(run_no_ar_level_direct, args)


if __name__ == "__main__":
    main()
