"""04 — API keys: create (with optional expiry), list, rotate with a grace
window, and revoke.

Agents authenticate with a user-scoped key (created from the dashboard) and can
mint narrower platform-scoped keys for specific integrations. This creates a
platform-scoped key with an `expires_at`, lists keys, rotates it with a bounded
`grace_seconds` window so the old key keeps validating during cut-over, then
revokes the replacement.

Requires a platform id — pass one as argv[1], or it uses your first platform.

    python 04_api_keys.py [platform_id]
"""

import datetime
import sys

from _common import banner, get_client, step


def main() -> None:
    api = get_client()
    banner("API keys — create / list / rotate / revoke")

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

    # expires_at: ISO-8601, naive treated as UTC, must be in the future.
    expires_at = (
        datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=90)
    ).isoformat()
    created = api.api_keys.create(
        scope="platform",
        platform_id=platform_id,
        name="SDK Example Key",
        expires_at=expires_at,
    )
    key_id = created["id"]
    # The plaintext key is only returned once, at creation.
    step(f"Created key #{key_id}, expires_at={created.get('expires_at')}; "
         f"token starts: {str(created.get('key', ''))[:8]}…")

    keys = api.api_keys.list()
    step(f"You now have {len(keys)} key(s).")

    # Rotate ahead of expiry with zero downtime: the new key validates
    # immediately; the old key keeps validating for `grace_seconds` (here 60s)
    # so in-flight callers can cut over before it dies like a revoked key.
    rotated = api.api_keys.rotate(key_id, grace_seconds=60)
    new_key_id = rotated["id"]
    old_key = rotated["old_key"]
    step(f"Rotated key #{key_id} -> #{new_key_id}; old key grace_until="
         f"{old_key['grace_until']}; new token starts: "
         f"{str(rotated.get('key', ''))[:8]}…")

    api.api_keys.revoke(new_key_id)
    step(f"Revoked key #{new_key_id}")

    print("\n✓ API key lifecycle complete.")


if __name__ == "__main__":
    main()
