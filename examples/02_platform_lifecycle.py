"""02 — Full platform lifecycle: build a neurosymbolic platform and query it.

The headline workflow:
    domain → ontology → dataset → build platform → wait → query (with explanation)

Builds a platform end-to-end, asks it a question, prints the explainable answer,
then deletes everything it created. The build can take a few minutes.

    python 02_platform_lifecycle.py
"""

import csv
import tempfile
from pathlib import Path

from _common import banner, get_client, step, wait_for_domain
from ambertraceai import AmbertraceError


def _make_graph_csv() -> str:
    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    )
    writer = csv.writer(fd)
    writer.writerow(["entity", "relation", "target"])
    writer.writerow(["Vendor", "bears", "UnlimitedLiability"])
    writer.writerow(["UnlimitedLiability", "increases", "Risk"])
    writer.writerow(["AutoRenewal", "increases", "Risk"])
    writer.writerow(["GoverningLaw", "constrains", "Vendor"])
    fd.close()
    return fd.name


def main() -> None:
    api = get_client()
    banner("Platform lifecycle — build & query")

    domain = api.domains.create(
        name="SDK Example — Risk Graph",
        description="Small risk ontology for the SDK platform example.",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}")

    csv_path = _make_graph_csv()
    dataset_id = None
    platform_id = None
    try:
        # Upload data first so the ontology builder can use it for validation.
        dataset = api.datasets.upload(
            domain_id=domain_id, file_path=csv_path, name="risk_graph.csv"
        )
        dataset_id = dataset["id"]
        step(f"Uploaded dataset #{dataset_id}")

        # Build the ontology (entities/relationships) from the description + data.
        # NOTE: build-ontology runs in the background and returns no job id, so we
        # poll the domain status rather than using wait_for_job. The platform build
        # requires the domain to be 'active' with at least one entity.
        api.domains.build_ontology(domain_id)
        domain = wait_for_domain(api, domain_id, timeout=240)
        step(f"Ontology build finished: domain status={domain.get('status')}")
        if domain.get("status") != "active":
            step("Domain did not become active; aborting build.")
            return

        result = api.platforms.create(domain_id=domain_id, dataset_id=dataset_id)
        platform_id = result["platform"]["id"]
        build_job_id = result["build_job"]["id"]
        step(f"Building platform #{platform_id} (job #{build_job_id})…")

        job = api.wait_for_job(build_job_id, timeout=600)
        step(f"Build finished: status={job.get('status')}")
        if job.get("status") in ("error", "failed"):
            step(f"Build error: {job.get('error_message')}")

        platform = api.platforms.get(platform_id)
        if platform.get("status") in ("active", "ready"):
            step("Querying the platform…")
            answer = api.platforms.query(
                platform_id, query="What increases risk?"
            )
            print(f"\n      Answer: {answer.get('answer')}\n")
            # `explanation` is a structured object: confidence + reasoning traces.
            exp = answer.get("explanation") or {}
            conf = exp.get("confidence", {})
            sym = exp.get("symbolic_trace", {})
            neu = exp.get("neural_trace", {})
            step(f"Confidence: {conf.get('overall')} "
                 f"(neural={conf.get('neural_confidence')}, symbolic={conf.get('symbolic_confidence')})")
            step(f"Symbolic rules fired: {sym.get('rules_fired')}/{sym.get('rules_evaluated')}")
            step(f"Neural nodes retrieved: {neu.get('nodes_retrieved')}")
        else:
            step(f"Platform not queryable (status={platform.get('status')}).")
    except AmbertraceError as e:
        print(f"\n  ! API error {e.status_code} ({e.code}): {e}")
        raise
    finally:
        Path(csv_path).unlink(missing_ok=True)
        # Clean up: delete the platform (removes its build jobs, rules,
        # predictions, reports, and platform-scoped keys), then dataset + domain.
        if platform_id:
            api.platforms.delete(platform_id)
            step(f"Deleted platform #{platform_id}")
        if dataset_id:
            api.datasets.delete(dataset_id)
        api.domains.delete(domain_id)
        step(f"Cleaned up dataset + domain #{domain_id}")

    print("\n✓ Platform lifecycle complete (resources cleaned up).")


if __name__ == "__main__":
    main()
