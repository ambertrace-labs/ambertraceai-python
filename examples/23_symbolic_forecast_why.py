"""23 — Symbolic forecast WHY + residual drift/correction diagnosis (preview).

The prediction "why" layer is a STANDALONE, fully-transparent forecasting mode:
the forecast is composed as ``baseline (persistence) + Σ fired driver-rules`` over
your data's REAL features, so the response carries an actionable *why* — the
ordered drivers that fired, each with its fitted contribution and reliability —
not just a number. With ``verified=True`` the active-driver set is run through
the verified kernel and each driver is stamped ``proof_checked``.

When a forecast misses badly, ``residual_diagnosis`` calls **drift vs
correction**: a decayed driver that pointed the wrong way => drift (residual
likely to keep widening); the still-reliable drivers point counter to the move
=> correction (target dislocated; residual likely to tighten).

This is a PREVIEW surface — the server gates it behind the
``AMBERTRACE_SYMBOLIC_FORECAST`` feature flag, so the calls raise
``AmbertraceError(404)`` when the feature is disabled on your platform.

    python 23_symbolic_forecast_why.py [platform_id]
"""

import sys

from _common import banner, get_client, step
from ambertraceai import AmbertraceError


def _pick_platform(api, argv) -> int | None:
    if len(argv) > 1:
        return int(argv[1])
    for p in api.platforms.list():
        if p.get("status") in ("active", "ready"):
            return p["id"]
    return None


def main() -> None:
    api = get_client()
    banner("Symbolic forecast WHY + residual diagnosis (preview)")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform — run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    configs = api.predictions.list_configs(platform_id)
    if not configs:
        print("  No prediction configs — run 06_predictions.py first to create one.")
        return
    config_id = configs[0]["id"]
    step(f"Using prediction config #{config_id}")

    try:
        # 1) Symbolic forecast with a proof-carrying WHY.
        result = api.predictions.symbolic_forecast(
            platform_id, prediction_config_id=config_id, verified=True,
        )
        fc = result["forecast"]
        step(
            f"Forecast value={fc['value']} "
            f"[{fc['lower']}, {fc['upper']}] (baseline={result['baseline']}, "
            f"skill_vs_persistence={result['skill_vs_persistence']})"
        )
        step(f"WHY — {len(result['why'])} driver(s) fired:")
        for w in result["why"]:
            mark = "proof-carrying" if w.get("proof_checked") else "fitted-only"
            print(
                f"    - {w['driver']}  "
                f"(direction={w['direction']}, contribution={w['contribution']}, "
                f"{mark})"
            )
        cert = result.get("why_certification")
        if cert:
            step(f"Certification: {cert.get('proof_summary')}")

        # 2) Residual diagnosis on a constructed breach (what-if value+actual).
        #    Use the forecast value as the issued value and a far-off actual so the
        #    breach gate trips, then read the drift/correction call.
        actual = fc["value"] + 5.0 * (abs(fc["value"]) + 1.0)
        diag = api.predictions.residual_diagnosis(
            platform_id, prediction_config_id=config_id,
            value=fc["value"], actual=actual, k=2.0,
        )
        step(
            f"Residual={diag['residual']} z={diag['z']} "
            f"breached={diag['breached']} => diagnosis={diag['diagnosis']}"
        )
        if diag.get("decayed_drivers"):
            step(f"Decayed drivers: {[d['name'] for d in diag['decayed_drivers']]}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
        if e.status_code == 404:
            print("  (The symbolic-forecast preview feature may be disabled on this platform.)")

    print("\n✓ Symbolic-forecast WHY walkthrough complete.")


if __name__ == "__main__":
    main()
