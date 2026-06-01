"""05 — Rule discovery: ask the platform to suggest symbolic rules.

Neurosymbolic platforms can propose human-readable rules from the data. This
requests suggestions and lists them. Operates on an existing platform — pass a
platform id as argv[1], or it uses your first active platform.

    python 05_rules_and_suggestions.py [platform_id]
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
    banner("Rule discovery — suggestions")

    platform_id = _pick_platform(api, sys.argv)
    if platform_id is None:
        print("  No active platform — run 02_platform_lifecycle.py first, or pass a id.")
        return
    step(f"Using platform #{platform_id}")

    suggestion_run = api.platforms.suggest_rules(platform_id, max_suggestions=3)
    job_id = suggestion_run.get("job_id") or (suggestion_run.get("job") or {}).get("id")
    if job_id:
        api.wait_for_job(job_id, timeout=180)
        step("Suggestion run finished.")

    suggestions = api.platforms.list_suggestions(platform_id)
    step(f"{len(suggestions)} suggestion(s):")
    for s in suggestions[:5]:
        print(f"      #{s.get('id')}: {s.get('description') or s.get('rule')}")

    # CONVENIENCE GAP: the API exposes
    #   POST /platforms/{id}/suggestions/{rid}/approve
    #   POST /platforms/{id}/suggestions/{rid}/reject
    # but the convenience layer has no approve_suggestion/reject_suggestion yet.
    # Until then, approving a suggestion requires the generated client.
    print("\n  (Approving/rejecting suggestions is not yet in the convenience layer.)")

    print("\n✓ Rule suggestion walkthrough complete.")


if __name__ == "__main__":
    main()
