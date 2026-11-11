"""80 -- AI-compute market data connector: GPU rental prices + LLM token prices.

The ``ai_compute`` connector is keyless and serves two CC BY 4.0 sources (attribution
required -- the connector listing carries the notice in ``source_notice``):

* GPU rental prices from FastGPU (https://fastgpu.co/dataset): daily fixings per GPU
  model -- columns ``{gpu_slug}_floor_usd_hr`` / ``_median_usd_hr`` / ``_spot_usd_hr``
  (``gpu_price_type="daily"`` gives per-provider prices instead).
* LLM token prices from ModelPriceWatch (https://modelpricewatch.com): the chain-linked
  LLM Price Index (``llm_price_index``, ``n_constituents``), or with
  ``token_price_type="models"`` per-model ``{model_id}_input`` / ``_output`` prices per
  million tokens (optionally ``token_providers``).

``data_type`` is ``gpu_prices``, ``token_prices`` or ``both``. This example lists the
connector by ``asset_class="ai-compute"``, fetches GPU fixings, then the token index.

    python 80_ai_compute_connector.py
"""

from _common import banner, get_client, print_dataset, step, wait_for_dataset
from ambertraceai import AmbertraceError


def main() -> None:
    api = get_client()
    banner("AI-compute market data (GPU prices + LLM token prices)")

    found = api.connectors.list(asset_class="ai-compute")
    step(f"Connectors for asset_class='ai-compute': {[c['type'] for c in found]}")
    for c in found:
        step(f"  {c['type']}: {c.get('source_notice')}")

    domain = api.domains.create(
        name="SDK Example — AI Compute Prices",
        description="GPU rental price fixings and the LLM Price Index.",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    try:
        for label, config in (
            ("GPU fixings", {"data_type": "gpu_prices", "gpu_models": ["h100-sxm", "a100-80gb"]}),
            ("LLM Price Index", {"data_type": "token_prices", "token_price_type": "index"}),
        ):
            step(f"Fetching {label}...")
            dataset = api.datasets.fetch(
                domain_id=domain_id, connector_type="ai_compute", config=config,
            )
            dataset = wait_for_dataset(api, dataset["id"])
            print_dataset(dataset)
            cols = [c.get("name") for c in (dataset.get("schema_info") or {}).get("columns", [])]
            step(f"Columns: {cols}")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
    finally:
        api.domains.delete(domain_id)
        step(f"Cleaned up domain #{domain_id}")

    print("\n✓ AI-compute walkthrough complete.")


if __name__ == "__main__":
    main()
