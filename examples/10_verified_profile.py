"""10 — Verified profile: proof-carrying queries and drift monitoring.

Builds a platform with the verified profile enabled — queries return a
proof certificate, and the drift endpoints let you monitor for behavioural
drift after approval.

Requires a working domain + dataset. Self-cleans.

    python 10_verified_profile.py
"""

import csv
import io
import tempfile

from _common import banner, get_client, step, wait_for_domain


def main() -> None:
    api = get_client()
    banner("Verified profile — proof certificates + drift monitoring")

    # ── 1. Create domain & dataset ──────────────────────────────────────

    step("Creating domain...")
    domain = api.domains.create(
        name="Access Control (Verified Demo)",
        description=(
            "A role-based access control domain with users, roles, and permissions. "
            "Users are assigned roles; roles grant permissions to resources. "
            "Safety property: the 'delete' permission must never be granted unconditionally."
        ),
    )
    domain_id = domain["id"]
    step(f"Domain #{domain_id} created.")

    step("Building ontology...")
    api.domains.build_ontology(domain_id)
    domain = wait_for_domain(api, domain_id)
    step(f"Ontology status: {domain['status']}")

    step("Uploading dataset...")
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["user", "role", "resource", "permission"])
    writer.writerows([
        ["alice", "admin", "reports", "read"],
        ["alice", "admin", "reports", "write"],
        ["bob", "viewer", "reports", "read"],
        ["carol", "editor", "documents", "read"],
        ["carol", "editor", "documents", "write"],
    ])
    tmp = tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w")
    tmp.write(buf.getvalue())
    tmp.close()
    dataset = api.datasets.upload(domain_id=domain_id, file_path=tmp.name, name="rbac_demo.csv")
    dataset_id = dataset["id"]
    step(f"Dataset #{dataset_id} uploaded.")

    # ── 2. Build a verified platform ────────────────────────────────────

    step("Building verified platform...")
    build = api.platforms.create(
        domain_id=domain_id,
        dataset_id=dataset_id,
        name="RBAC Verified Demo",
        verified_profile=True,
        verified_min_confidence=0.85,
        invariant_manifest=[
            {
                "name": "no_unconditional_delete",
                "kind": "forbid",
                "target": "permit_delete",
                "assumed_absent": ["permit_delete"],
            },
        ],
    )
    job_id = build.get("job_id") or (build.get("job") or {}).get("id")
    if job_id:
        api.wait_for_job(job_id, timeout=300)
    platform = api.platforms.get(build["id"])
    platform_id = platform["id"]
    verified = platform.get("verified_profile", False)
    step(f"Platform #{platform_id} built (verified_profile={verified}).")

    # ── 3. Query with proof certificate ─────────────────────────────────

    step("Querying verified platform...")
    result = api.platforms.query(platform_id, query="What permissions does alice have?")
    step(f"Answer: {result.get('answer', '(no answer)')[:120]}")
    step(f"proof_checked: {result.get('proof_checked')}")
    if result.get("proof_summary"):
        step(f"proof_summary: {result['proof_summary'][:200]}")

    # ── 4. Rules CRUD ───────────────────────────────────────────────────

    step("Listing rules...")
    rules = api.platforms.list_rules(platform_id)
    step(f"{len(rules)} active rule(s).")

    step("Creating a new rule...")
    new_rule = api.platforms.create_rule(
        platform_id,
        name="viewer_read_only",
        description="Viewers can only read, never write.",
        condition={"field": "role", "operator": "==", "value": "viewer"},
        action={"type": "derive", "value": "read_only"},
    )
    rule_id = new_rule["id"]
    step(f"Rule #{rule_id} created.")

    step("Updating rule description...")
    api.platforms.update_rule(platform_id, rule_id, description="Viewers are restricted to read-only access.")
    step("Updated.")

    step("Deleting rule...")
    api.platforms.delete_rule(platform_id, rule_id)
    step("Deleted.")

    # ── 5. Drift monitoring ─────────────────────────────────────────────

    step("Capturing drift baseline (approval time)...")
    baseline = api.platforms.capture_drift_baseline(platform_id)
    step(f"Baseline: {baseline.get('certified_rejection_rate', 'n/a')} rejection rate, "
         f"{baseline.get('n', 0)} samples.")

    step("Checking for drift...")
    drift = api.platforms.check_drift(platform_id)
    step(f"drift_detected: {drift.get('drift_detected', False)}")
    for alert in drift.get("alerts", []):
        print(f"      ALERT: {alert.get('signal')} — {alert.get('message', '')}")

    # ── 6. Update verified settings ─────────────────────────────────────

    step("Updating confidence threshold...")
    api.platforms.update(platform_id, verified_min_confidence=0.90)
    updated = api.platforms.get(platform_id)
    step(f"New tau: {updated.get('config', {}).get('verified_min_confidence', '?')}")

    # ── Cleanup ─────────────────────────────────────────────────────────

    step("Cleaning up...")
    api.platforms.delete(platform_id)
    api.datasets.delete(dataset_id)
    api.domains.delete(domain_id)
    step("All resources deleted.")

    print("\n✓ Verified profile walkthrough complete.")


if __name__ == "__main__":
    main()
