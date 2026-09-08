"""46 -- Tiered coverage forecast with neural confidence gate.

Demonstrates the ``neural_confidence_tau`` config parameter that activates
the per-point GBT neural-tier confidence gate:

- **tau=0.0** (default) -- the gate labels every prediction with its
  ``forecast_tier`` and ``confidence`` but does NOT distinguish below-tau
  predictions. Backward-compatible: the ``value`` is always the GBT output.
- **tau>0** (e.g. 0.5) -- below-tau GBT predictions are served with
  ``forecast_tier='neural_weak'`` and ``neural_confidence_tau=<tau>`` so
  consumers can distinguish strong from weak neural predictions. The raw
  GBT value is always served -- never replaced.

The two-axis gate (Axis A: in-training-range OOD gate; Axis B: interval
sharpness) mirrors the ``ScoredDetermination`` trust-tier pattern
(example 41) but for regressors, not classifiers.

The coverage certificate's TOTALITY claim (every holdout point served by a
named tier with a finite value, ``n_uncovered == 0``) is KERNEL-CERTIFIED:
``coverage_certificate.proof_ref`` carries the verdict of the trusted
symbolic kernel -- the same kernel that certifies rule firings -- with
``claim='coverage_totality'``. An uncovered point fails the proof closed.

    python 46_tiered_coverage_forecast.py [platform_id]
"""

import sys

from _common import banner, get_client, step


def _pick_platform(api, argv) -> int | None:
    if len(argv) > 1:
        return int(argv[1])
    for p in api.platforms.list():
        if p.get("status") in ("active", "ready"):
            return p["id"]
    return None


def main() -> None:
    api = get_client()
    banner("Tiered coverage forecast -- neural confidence gate")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform -- run 02_platform_lifecycle.py first, or pass an id.")
        return
    step(f"Using platform #{platform_id}")

    # Find or create a prediction config with the confidence gate active.
    # neural_confidence_tau=0.5 means: GBT predictions with two-axis
    # confidence >= 0.5 are admitted as 'neural_scored'; below 0.5
    # the raw GBT prediction is served as 'neural_weak'.
    configs = api.platforms.list_prediction_configs(platform_id)
    config_id = None
    for c in configs:
        if c.get("neural_confidence_tau", 0.0) > 0:
            config_id = c["id"]
            break

    if config_id is None:
        step("Creating a prediction config with neural_confidence_tau=0.5")
        try:
            config = api.platforms.create_prediction_config(
                platform_id,
                target_field="value",
                time_index_field="date",
                horizon=1,
                frequency="monthly",
                neural_confidence_tau=0.5,
            )
            config_id = config["id"]
            step(f"  Created config #{config_id}")
        except Exception as e:
            print(f"  Could not create config: {e}")
            return

    # Run a prediction -- the response now carries tiering fields.
    step(f"Running prediction with config #{config_id}")
    try:
        result = api.platforms.predict(
            platform_id, prediction_config_id=config_id, explain=False,
        )
    except Exception as e:
        print(f"  Prediction failed: {e}")
        return

    pred = result.get("prediction", {})
    step("Prediction result:")
    print(f"  value           : {pred.get('value')}")
    print(f"  forecast_tier   : {pred.get('forecast_tier')}")
    print(f"  confidence      : {pred.get('confidence')}")
    print(f"  value_space     : {pred.get('value_space')}")

    basis = pred.get("confidence_basis")
    if basis:
        step("Confidence basis (two-axis gate):")
        print(f"  method          : {basis.get('method')}")
        print(f"  in_range        : {basis.get('in_range')}")
        print(f"  tau             : {basis.get('tau')}")
        print(f"  certified       : {basis.get('certified')}")
        if basis.get("uncertified_reason"):
            print(f"  reason          : {basis.get('uncertified_reason')}")

    # Request the symbolic-forecast with fitted_series to get the
    # coverage certificate + per-tier skill reporting. The certificate tells a
    # consumer what fraction of holdout points were served by each tier, and
    # per-tier skill shows how each tier performed independently.
    step("Requesting symbolic-forecast with coverage certificate")
    try:
        sf = api.platforms.symbolic_forecast(
            platform_id,
            prediction_config_id=config_id,
            include_fitted_series=True,
        )
    except Exception as e:
        print(f"  Symbolic forecast failed: {e}")
        return

    cert = sf.get("coverage_certificate")
    if cert:
        step("Coverage certificate:")
        print(f"  n_points        : {cert.get('n_points')}")
        print(f"  n_uncovered     : {cert.get('n_uncovered')}")
        print(f"  coverage_total  : {cert.get('coverage_total')}")
        print(f"  tiers_present   : {cert.get('tiers_present')}")
        for tier_name, tier_info in (cert.get("tiers") or {}).items():
            print(f"    {tier_name:25s}: n={tier_info['n']}, "
                  f"fraction={tier_info['fraction']}")

        # The totality claim itself is KERNEL-CERTIFIED: proof_ref carries
        # the verdict of the trusted symbolic kernel proving that every
        # holdout point resolved to a tier with a finite value -- the same
        # kernel that certifies rule firings. Values remain fitted-not-proven.
        proof_ref = cert.get("proof_ref")
        if proof_ref:
            step("Totality proof (kernel-certified):")
            print(f"  claim           : {proof_ref.get('claim')}")
            print(f"  proof_checked   : {proof_ref.get('proof_checked')}")
            print(f"  certified rows  : {proof_ref.get('n_certified_rows')}")
            print(f"  rejected rows   : {proof_ref.get('n_rejected_rows')}")
            print(f"  summary         : {proof_ref.get('proof_summary')}")
            for reason in proof_ref.get("reasons") or []:
                print(f"    reason        : {reason}")

    pts = sf.get("per_tier_skill")
    if pts:
        step("Per-tier skill:")
        for tier_name, metrics in pts.items():
            if metrics is None:
                continue
            print(f"  {tier_name}:")
            print(f"    n                     : {metrics.get('n')}")
            print(f"    skill_vs_persistence  : {metrics.get('skill_vs_persistence')}")
            print(f"    mae                   : {metrics.get('mae')}")
            print(f"    rmse                  : {metrics.get('rmse')}")

    # Per-point rule-firing annotations. Each series point carries
    # fired_rules (list of driver names whose condition held on that row)
    # and rule_layer_predicted (anchor + sum of fired effects — the
    # symbolic rule-layer-only prediction for that point).
    fs = sf.get("fitted_series")
    if fs:
        step("Per-point rule-firing annotations (first 5 holdout points):")
        for pt in (fs.get("series") or [])[:5]:
            fired = pt.get("fired_rules", [])
            rlp = pt.get("rule_layer_predicted")
            print(f"  index={pt['index']}  tier={pt.get('forecast_tier')}"
                  f"  fired_rules={fired}"
                  f"  rule_layer_predicted={rlp}"
                  f"  predicted={pt.get('predicted')}")

    step("Done.")


if __name__ == "__main__":
    main()
