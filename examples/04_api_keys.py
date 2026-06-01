"""04 — API keys: create a platform-scoped key, list, and revoke it.

Agents authenticate with a user-scoped key (created from the dashboard) and can
mint narrower platform-scoped keys for specific integrations. This creates a
platform-scoped key, lists keys, then revokes the one it created.

Requires a platform id — pass one as argv[1], or it uses your first platform.

    python 04_api_keys.py [platform_id]
"""

import sys

from _common import banner, get_client, step


def main() -> None:
    api = get_client()
    banner("API keys — create / list / revoke")

    # Resolve a platform id to scope the key to.
    if len(sys.argv) > 1:
        platform_id = int(sys.argv[1])
    else:
        platforms = api.platforms.list()
        if not platforms:
            print("  No platforms found — run 02_platform_lifecycle.py first, or "
                  "pass a platform id.")
            return
        platform_id = platforms[0]["id"]
    step(f"Using platform #{platform_id}")

    created = api.api_keys.create(
        scope="platform", platform_id=platform_id, name="SDK Example Key"
    )
    key_id = created["id"]
    # The plaintext key is only returned once, at creation.
    step(f"Created key #{key_id}; token starts: {str(created.get('key', ''))[:8]}…")

    keys = api.api_keys.list()
    step(f"You now have {len(keys)} key(s).")

    api.api_keys.revoke(key_id)
    step(f"Revoked key #{key_id}")

    print("\n✓ API key lifecycle complete.")


if __name__ == "__main__":
    main()
