"""09 — FRED analysis: explainable Q&A over real macro data.

Ingests FRED series, builds a neurosymbolic platform, and asks a natural-language
question — returning an answer with neural + symbolic reasoning traces. No model
training; this showcases the explainable query path on live economic data.

Bring your own FRED key in examples/.env:
    FRED_API_KEY=your_fred_key

    python 09_fred_analysis.py
"""

import os
import sys

from _common import banner, get_client, step, wait_for_domain
from ambertraceai import AmbertraceError

SERIES = ["GS10", "GS2", "FEDFUNDS", "UNRATE", "CPIAUCSL"]


def main() -> None:
    fred_key = os.environ.get("FRED_API_KEY")
    if not fred_key:
        sys.exit("Set FRED_API_KEY in examples/.env (free at https://fred.stlouisfed.org).")

    api = get_client()
    banner("FRED macro analysis")

    domain = api.domains.create(
        name="SDK Example — Macro Indicators",
        description=(
            "US macro indicators: 10y and 2y Treasury yields, fed funds rate, "
            "unemployment, and CPI. Used for explainable macro analysis."
        ),
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    platform_id = None
    try:
        dataset = api.datasets.fetch(
            domain_id=domain_id, connector_type="fred",
            config={"api_key": fred_key, "series_ids": SERIES, "frequency": "monthly"},
        )
        step(f"Ingested FRED data: dataset #{dataset.get('id')} ({SERIES})")

        api.domains.build_ontology(domain_id)
        if wait_for_domain(api, domain_id, timeout=240).get("status") != "active":
            step("Ontology build did not complete; aborting.")
            return

        result = api.platforms.create(domain_id=domain_id, dataset_id=dataset["id"])
        platform_id = result["platform"]["id"]
        api.wait_for_job(result["build_job"]["id"], timeout=600)
        step(f"Platform #{platform_id} built")

        answer = api.platforms.query(
            platform_id, query="What is the relationship between the fed funds rate and Treasury yields?",
        )
        print(f"\n      Answer: {answer.get('answer')}\n")
        exp = answer.get("explanation") or {}
        conf = exp.get("confidence", {})
        step(f"Confidence: {conf.get('overall')} "
             f"(neural={conf.get('neural_confidence')}, symbolic={conf.get('symbolic_confidence')})")
        step(f"Symbolic rules fired: {exp.get('symbolic_trace', {}).get('rules_fired')}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
    finally:
        # Delete the platform first (its children aren't covered by the domain
        # delete cascade), then the domain.
        if platform_id:
            api.platforms.delete(platform_id)
        api.domains.delete(domain_id)
        step(f"Cleaned up platform + domain #{domain_id}")

    print("\n✓ FRED analysis walkthrough complete.")


if __name__ == "__main__":
    main()
