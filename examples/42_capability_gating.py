"""42 -- Org-capability gating: discover capabilities and handle 403.

Ambertrace organisations can have individual capabilities (chat, query,
predictions) enabled or disabled by an administrator.  When a capability is
disabled for your organisation, every endpoint gated by that capability returns
HTTP 403 with a structured error body:

    {
      "error": {
        "code": "capability_disabled",
        "message": "This capability is not enabled for your organisation. ..."
      },
      "capability": "query"          # the gated capability name
    }

The ``capability`` field at the top level names which capability was denied,
so SDK callers can branch on it programmatically.

Discovery:
  GET /api/v1/capabilities  (user-scoped or session callers only)
  Returns {"capabilities": {"chat": true, "query": true, "predictions": false}, ...}

Platform-scoped API keys receive 403 "forbidden" on the discovery endpoint
(scope-context precedent) -- they are bound to a single platform and have no
org-wide visibility.  A platform-key caller should either:
  (a) use a user-scoped key for capability discovery, or
  (b) have an org administrator communicate the enabled set out of band.

This example demonstrates:
  1. Discovering the org's effective capability set.
  2. Handling the capability_disabled 403 on a gated endpoint (query).
  3. Branching on the structured error to give the user actionable guidance.

Requires a platform id -- pass one as argv[1], or it uses your first platform.

    python 42_capability_gating.py [platform_id]
"""

import sys

from _common import banner, get_client, step


def main():
    banner(__doc__)
    api = get_client()

    # ------------------------------------------------------------------ step 1
    step(1, "Discover the org's effective capabilities")
    try:
        caps = api._request("GET", "/api/v1/capabilities")
        effective = caps.get("capabilities", {})
        print("Effective capabilities:")
        for name, enabled in effective.items():
            status = "ENABLED" if enabled else "DISABLED"
            print(f"  {name}: {status}")
    except Exception as exc:
        # Platform-scoped keys get 403 forbidden here.
        print(f"Could not discover capabilities: {exc}")
        print("Tip: use a user-scoped API key for capability discovery.")
        effective = {}

    # ------------------------------------------------------------------ step 2
    step(2, "Resolve platform id")
    if len(sys.argv) > 1:
        platform_id = int(sys.argv[1])
    else:
        platforms = api.platforms.list()
        if not platforms:
            print("No platforms found -- create one first.")
            return
        platform_id = platforms[0]["id"]
    print(f"Using platform {platform_id}")

    # ------------------------------------------------------------------ step 3
    step(3, "Attempt a query (may be capability-gated)")
    from ambertraceai import AmbertraceError

    try:
        result = api.platforms.query(
            platform_id,
            query="What is the assessment?",
            facts={"score": 80},
        )
        print(f"Query succeeded: decision={result.get('decision')}")
    except AmbertraceError as e:
        if e.code == "capability_disabled":
            # The structured error carries the gated capability name.
            cap_name = getattr(e, "capability", None)
            print(f"Capability '{cap_name}' is disabled for this org.")
            print("Contact your org administrator to enable it,")
            print("or check GET /api/v1/capabilities for the current set.")
        else:
            print(f"Query failed: [{e.code}] {e}")

    # ------------------------------------------------------------------ step 4
    step(4, "Pre-flight check: skip gated calls if capability is known disabled")
    if effective.get("predictions") is False:
        print("Predictions capability is DISABLED -- skipping predict call.")
        print("This avoids a round-trip that would 403.")
    else:
        print("Predictions capability is enabled (or unknown) -- would proceed.")


if __name__ == "__main__":
    main()
