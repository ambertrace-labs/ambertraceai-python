"""60 -- Batch query + compact/projection mode.

Demonstrates two platform throughput features:

1. **Batch query** (``platforms.query_batch``): send N queries in one call
   instead of N round-trips. Each item is independent -- a failure in one item
   produces a per-item error, never a batch-level failure. Maximum 50 queries
   per batch.

2. **Projection mode**: request only the response fields you need (e.g.
   ``["decision", "proof_checked"]``) to shrink the payload. Works on BOTH
   the single-query and batch-query endpoints. Default (no projection) returns
   the full response -- existing callers are unaffected.

Requires an active platform with a decision layer. Pass a platform id as
argv[1], or uses your first active platform.

    python 60_batch_query_projection.py [platform_id]
"""

import sys

from _common import banner, get_client, step


def main():
    banner(__doc__)
    api = get_client()

    # ------------------------------------------------------------------ step 1
    step(1, "Resolve an active platform")
    if len(sys.argv) > 1:
        pid = int(sys.argv[1])
    else:
        platforms = api.platforms.list()
        active = [p for p in platforms if p.get("status") == "active"]
        if not active:
            print("No active platforms found. Build one first (see 02_platform_lifecycle.py).")
            return
        pid = active[0]["id"]
    print(f"  platform_id = {pid}")

    # ------------------------------------------------------------------ step 2
    step(2, "Single query with projection (compact response)")
    result = api.platforms.query(
        pid,
        query="What is the decision?",
        projection=["decision", "proof_checked"],
    )
    print(f"  decision:      {result.get('decision')}")
    print(f"  proof_checked: {result.get('proof_checked')}")
    # Non-requested fields are omitted from the response.
    assert "answer" not in result, "projection should have omitted 'answer'"
    print("  (answer, explanation omitted as expected)")

    # ------------------------------------------------------------------ step 3
    step(3, "Batch query -- 3 queries in one call")
    batch_result = api.platforms.query_batch(
        pid,
        queries=[
            {"query": "Classify scenario A"},
            {"query": "Classify scenario B"},
            {"query": "Classify scenario C"},
        ],
    )
    print(f"  platform_id: {batch_result['platform_id']}")
    for item in batch_result["results"]:
        status = item["status"]
        idx = item["index"]
        if status == "ok":
            d = item["data"]
            print(f"  [{idx}] ok — decision={d.get('decision')}, "
                  f"proof_checked={d.get('proof_checked')}")
        else:
            print(f"  [{idx}] error — {item['error']}")

    # ------------------------------------------------------------------ step 4
    step(4, "Batch query with batch-level projection")
    compact = api.platforms.query_batch(
        pid,
        queries=[
            {"query": "Classify scenario A"},
            {"query": "Classify scenario B"},
        ],
        projection=["decision", "proof_checked"],
    )
    for item in compact["results"]:
        if item["status"] == "ok":
            d = item["data"]
            assert "answer" not in d, "batch projection should omit 'answer'"
            print(f"  [{item['index']}] decision={d.get('decision')}")

    # ------------------------------------------------------------------ step 5
    step(5, "Per-item projection override")
    mixed = api.platforms.query_batch(
        pid,
        queries=[
            {"query": "Classify A"},  # inherits batch projection
            {"query": "Classify B", "projection": ["answer"]},  # overrides
        ],
        projection=["decision"],
    )
    item_0 = mixed["results"][0]["data"]
    item_1 = mixed["results"][1]["data"]
    print(f"  item 0 has decision: {'decision' in item_0}")
    print(f"  item 1 has answer:   {'answer' in item_1}")
    print(f"  item 1 has decision: {'decision' in item_1}")  # overridden out

    print("\nDone.")


if __name__ == "__main__":
    main()
