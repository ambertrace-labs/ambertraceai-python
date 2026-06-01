"""01 — Domains and data: create a domain, upload a dataset, inspect quality.

Demonstrates the first half of the workflow: defining a domain of expertise and
getting data in. Creates a domain + dataset, runs a quality report and a preview,
then deletes everything it created.

    python 01_domain_and_data.py
"""

import csv
import tempfile
from pathlib import Path

from _common import banner, get_client, step


def _make_sample_csv() -> str:
    """Write a tiny contracts-style CSV to a temp file and return its path."""
    fd = tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, newline=""
    )
    writer = csv.writer(fd)
    writer.writerow(["clause", "category", "risk_score"])
    writer.writerow(["Unlimited liability for vendor", "liability", "0.91"])
    writer.writerow(["Auto-renewal without notice", "term", "0.74"])
    writer.writerow(["Governing law: Delaware", "jurisdiction", "0.10"])
    writer.writerow(["Net-90 payment terms", "payment", "0.55"])
    fd.close()
    return fd.name


def main() -> None:
    api = get_client()
    banner("Domain + data lifecycle")

    domain = api.domains.create(
        name="SDK Example — Contracts",
        description="Contract clause analysis for risk and compliance (SDK example).",
    )
    domain_id = domain["id"]
    step(f"Created domain #{domain_id}: {domain['name']}")

    csv_path = _make_sample_csv()
    try:
        dataset = api.datasets.upload(
            domain_id=domain_id,
            file_path=csv_path,
            name="contracts_sample.csv",
        )
        dataset_id = dataset["id"]
        step(f"Uploaded dataset #{dataset_id} ({dataset.get('name')})")

        preview = api.datasets.preview(dataset_id)
        cols = preview.get("columns") or preview.get("schema") or []
        step(f"Preview columns: {cols}")

        quality = api.datasets.quality(dataset_id)
        score = quality.get("score") or quality.get("overall_score")
        step(f"Quality report: score={score}")

        step("Cleaning dataset…")
        clean_result = api.datasets.clean(dataset_id)
        # Cleaning may run asynchronously and return a job.
        job_id = clean_result.get("job_id") or (clean_result.get("job") or {}).get("id")
        if job_id:
            job = api.wait_for_job(job_id, timeout=120)
            step(f"Clean job finished: status={job.get('status')}")
        else:
            step("Clean completed synchronously.")

        api.datasets.delete(dataset_id)
        step(f"Deleted dataset #{dataset_id}")
    finally:
        Path(csv_path).unlink(missing_ok=True)
        api.domains.delete(domain_id)
        step(f"Deleted domain #{domain_id}")

    print("\n✓ Domain + data lifecycle complete (resources cleaned up).")


if __name__ == "__main__":
    main()
