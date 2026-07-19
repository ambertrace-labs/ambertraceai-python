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

from _common import banner, get_client, step
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
        # build-ontology runs in the background and returns a 202 job envelope with
        # a stable job_id — poll it with wait_for_job (which raises if the build
        # fails). The platform build then requires the domain to be 'active' with
        # at least one entity.
        onto = api.domains.build_ontology(domain_id)
        api.wait_for_job(onto.job_id, timeout=240)
        domain = api.domains.get(domain_id)
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

        # BUILD QUALITY — the customer-facing structural-health summary. This is
        # the honest, label-free substitute for an accuracy number (which can't
        # transfer to your domain): status is needs_review whenever a *blocking*
        # check fails (no certification / a declared decision class is
        # unreachable / no restrictive decision so it permits everything).
        # It lives on the *platform build* job result and is also persisted on
        # the platform (api.platforms.build_quality / .blocking_checks).
        bq = (job.get("result") or {}).get("build_quality") or {}
        if bq:
            step(f"Build quality: {bq.get('status')}")
            for chk in bq.get("checks", []):
                if not chk.get("ok"):
                    step(f"  [{chk.get('severity')}] {chk.get('id')}: {chk.get('detail')}")
            blocking = api.platforms.blocking_checks(platform_id)
            if blocking:
                step(f"This build needs review — {len(blocking)} blocking issue(s).")

        # The same build job result also carries `generation_diagnostics` — the
        # decision-coverage detail behind build_quality: how many rules were
        # generated and whether the rule set can reach an adverse decision. NB:
        # this lives on the *platform build* job — the ontology build job does
        # not carry it.
        diag = (job.get("result") or {}).get("generation_diagnostics") or {}
        if diag:
            step(f"Generated {diag.get('rule_count')} rules "
                 f"({diag.get('classifier_count')} classifiers, "
                 f"{diag.get('verdict_conclusion_count')} deny/block conclusions)")
            if not diag.get("can_decide_adversely", True):
                # No deny/block conclusion → the platform permits everything.
                step("This platform reaches NO adverse decision (permits everything).")
                for w in diag.get("decision_coverage_warnings", []):
                    step(f"  coverage warning: {w}")

        # STATED-CONSTRAINT DIAGNOSTIC — after the ontology build, the domain
        # detail carries an advisory diagnostic listing constraints the description
        # states but no rule encodes (e.g. "debt <= 40% of income" with no
        # cross-field coefficient rule). Absent when all constraints are encoded.
        domain_detail = api.domains.get(domain_id)
        sc_diag = (domain_detail.get("ontology") or {}).get(
            "stated_constraint_diagnostics")
        if sc_diag:
            step(f"Stated-constraint diagnostic: {len(sc_diag)} unencoded constraint(s)")
            for f in sc_diag:
                step(f"  {f['comparison_field']} {f.get('direction')} "
                     f"{f.get('coefficient')}*{f['coefficient_field']}")

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
