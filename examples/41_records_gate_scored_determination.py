"""41 — Records-disclosure gate with an OPEN-TEXTURED scored determination.

The Privacy Act (5 U.S.C. 552a) lets a federal agency disclose records for a "routine
use" ONLY where the use is *compatible with* the purpose for which the record was
collected (552a(a)(7)). "Compatible" is the textbook OPEN-TEXTURED predicate: no
bright-line rule decides it -- a disclosure in the same subject area can still be
INCOMPATIBLE if it betrays the collection purpose (selling licensing records to a data
broker), while a different-looking use can be compatible (continuing a patient's care).

This example shows the ``scored_determinations`` capability: where deduction is silent,
the platform's OWN runtime LLM is given the compatibility doctrine + the situation TEXT
and returns a *calibrated probability* the use is compatible, admitted as a
confidence-carrying fact subject to the fact-gate threshold τ
(``verified_min_confidence``). Then ORDINARY rules decide:

  * ``compatibility_established`` (the scored head) with ``p >= τ`` -> ``routine_use_basis``
    derives -> **permit**;
  * ``p < τ`` OR an abstain / out-of-distribution / high self-consistency dispersion
    determination admits NO fact -> ``routine_use_unverified`` derives (it is NOT
    established) -> **escalate**, never a permit.

DEDUCTIVE-FIRST, fail-closed: the LLM-τ score fills ONLY the open-textured joint, and
even there it certifies only when it is coherent, in-regime, and above τ -- otherwise the
request routes to a human. The score is SERVER-COMPUTED from the text; a caller cannot
hand-set it. Its guarantee is EMPIRICAL (calibration-in-regime + coherent-input +
fail-closed-OOD) -- honestly WEAKER than the deductive kernel proofs.

THE DECISIVE EXHIBIT
--------------------
The SAME routine-use request shape is decided PURELY by whether the compatibility
determination clears τ:
  * medical-continuity (compatible) -> PERMIT, the accepted determination + its score in
    the proof;
  * DMV-to-data-broker (incompatible) -> ESCALATE, the rejected call surfaced in
    ``explanation.rejected_facts`` + ``explanation.scored_determinations``;
  * an off-topic use (out of distribution) -> the scorer ABSTAINS -> ESCALATE.

Illustrative encoding for demonstration -- not legal advice.

    python 41_records_gate_scored_determination.py            # build + decide (verified)
    python 41_records_gate_scored_determination.py --standard # skip the verified profile
"""

from __future__ import annotations

import argparse
from pathlib import Path

from _common import (
    add_common_args,
    add_verified_args,
    build_ontology,
    print_dataset,
    print_ontology,
    print_section,
    run_demo,
)

DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "records_disclosure_cases.csv"

DOMAIN_NAME = "Privacy Act records-disclosure routine-use gate"
DOMAIN_DESCRIPTION = (
    "Decide whether a federal agency may disclose records for a proposed routine use; the "
    "outcome is permit or escalate. Each request has a stated_purpose (the proposed use, free "
    "text), a collection_purpose (why the records were originally collected, free text), and the "
    "flag routine_use_claimed (the agency claims a routine-use basis). "
    "Classify these named conditions: the routine use has a basis when routine_use_claimed is "
    "true and compatibility_established is true; the routine use is unverified when "
    "routine_use_claimed is true and compatibility_established is not true. "
    "Decide the outcome by the first matching rule: permit when the routine use has a basis; "
    "escalate when the routine use is unverified; otherwise escalate."
)

# The open-textured scored determination — the platform's runtime LLM scores the
# compatibility predicate, admitted as a τ-gated fact keyed `compatibility_established`.
SCORED_DETERMINATIONS = {
    "enabled": True,
    "determinations": [{
        "head": "compatibility_established",
        "question": ("Is the PROPOSED USE compatible with the ORIGINAL COLLECTION PURPOSE "
                     "under the Privacy Act routine-use compatibility test (5 U.S.C. "
                     "552a(a)(7))?"),
        "doctrine": (
            "You assess a single, narrow legal predicate under the Privacy Act of 1974. A "
            "federal agency holds records collected for one stated purpose and proposes to "
            "disclose them for a different use, relying on the 'routine use' exception "
            "(552a(b)(3)), lawful ONLY where the proposed use is COMPATIBLE with the purpose "
            "for which the record was collected (the 552a(a)(7) compatibility test). "
            "'Compatible' is narrower than merely 'related' or 'same topic': it asks whether "
            "the new use is consistent with the reasonable expectations of the individual and "
            "the original collection purpose. A use in the same subject area can still be "
            "INCOMPATIBLE if it betrays the purpose of collection (e.g. selling records "
            "collected for licensing to a data broker). Reason ONLY about compatibility of "
            "PURPOSES, not topical similarity of words."),
        "situation_fields": {
            "ORIGINAL COLLECTION PURPOSE": "collection_purpose",
            "PROPOSED USE (the disclosure being contemplated)": "stated_purpose",
        },
        "true_value": True,
        "dispersion_escalate": 0.15,
    }],
}


def _facts(collection: str, proposed: str) -> dict:
    return {
        "routine_use_claimed": True,
        "collection_purpose": collection,
        "stated_purpose": proposed,
    }


# (label, expected verdict, facts) — the decisive exhibit: verdict flips purely on the score.
SHOWCASE = [
    ("1. Medical continuity: release treatment history to a referred specialist (COMPATIBLE)",
     "permit",
     _facts("Health records collected to provide medical treatment to the patient.",
            "Releasing a patient's treatment history to a referred specialist continuing "
            "that patient's care.")),
    ("2. DMV to data broker: sell licence photos to a commercial data broker (INCOMPATIBLE)",
     "escalate",
     _facts("Records collected to license and register motor-vehicle operators.",
            "Selling drivers' licence photos and addresses to a commercial data broker.")),
    ("3. Tax administration: disclose income records to enforce tax law (COMPATIBLE)",
     "permit",
     _facts("Records were collected to administer federal income tax obligations.",
            "Disclosing income records to the state tax authority to administer and "
            "enforce tax law.")),
    ("4. Census to immigration enforcement: hand responses to deportation targeting (INCOMPAT)",
     "escalate",
     _facts("Responses collected solely to produce anonymous population statistics.",
            "Handing census household responses to immigration agents for deportation "
            "targeting.")),
]


def _decide(api, pid: int, label: str, expected: str, facts: dict) -> bool:
    try:
        report = api.platforms.query(
            pid, query="May the agency disclose these records for this use?", facts=facts)
    except Exception as exc:  # a verified fail-safe refusal is an outcome, not a crash
        print(f"  {label}\n    VERIFIED FAIL-SAFE — refused to certify: {exc}")
        return False
    outcome = str(report.get("decision"))
    ok = outcome == expected
    mark = "OK" if ok else f"!! expected {expected}"
    pc = report.get("proof_checked")
    # surface the scored determination's calibrated probability + certified? flag
    sd = (report.get("explanation") or {}).get("scored_determinations") or []
    score_str = ""
    if sd:
        d0 = sd[0]
        p = d0.get("probability")
        score_str = (f"  compat p={p:.2f} certified={d0.get('certified')}"
                     if p is not None
                     else f"  compat UNCERTIFIED ({d0.get('uncertified_reason')})")
    print(f"  {label}\n    -> {outcome.upper():8s} [{mark}]  proof_checked={pc}{score_str}")
    return ok


def run_records_gate(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Creating the records-disclosure routine-use domain")
    domain = api.domains.create(name=DOMAIN_NAME, description=DOMAIN_DESCRIPTION)
    dataset = api.datasets.upload(domain_id=domain["id"], file_path=str(args.dataset))
    print_dataset(dataset)

    print_section(2, total, "Building ontology (classify-then-conclude gate)")
    domain = build_ontology(api, domain["id"])
    print_ontology(domain, limit=12)

    print_section(3, total, "Building verified platform + wiring the scored determination")
    verified = not args.standard
    extra = {"verified_profile": True, "verified_min_confidence": args.tau,
             "scored_determinations": SCORED_DETERMINATIONS} if verified else {}
    resp = api.platforms.create(domain_id=domain["id"], dataset_id=dataset["id"], **extra)
    pid = resp["id"]
    api.wait_for_job(resp.job_id)
    # scored_determinations is also settable post-hoc via platforms.update:
    #   api.platforms.update(pid, scored_determinations=SCORED_DETERMINATIONS)
    platform = api.platforms.get(pid)
    print(f"  Platform {pid}: {platform['name']} ({platform.get('status')}) — "
          f"scored determination {'ON' if verified else 'OFF (standard build)'}")

    print_section(4, total, "Deciding disclosures (each verdict decided purely by the score vs τ)")
    correct = 0
    for label, expected, facts in SHOWCASE:
        correct += _decide(api, pid, label, expected, facts)
    print(f"\n{correct}/{len(SHOWCASE)} disclosures decided as the compatibility test requires. "
          f"Platform {pid}. Compatible uses PERMIT (p >= τ); incompatible / un-assessable uses "
          "ESCALATE — the score fills the open-textured joint, deductive-first and fail-closed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Privacy Act records-disclosure routine-use gate — AmberTrace AI verified "
                    "permit/escalate with an OPEN-TEXTURED scored determination (the "
                    "compatibility joint scored by the platform's own runtime LLM, τ-gated). "
                    "Illustrative encoding for demonstration — not legal advice.")
    add_common_args(parser)
    add_verified_args(parser)
    parser.add_argument(
        "--dataset", type=Path, default=DEFAULT_DATASET,
        help="CSV file to upload (default: records_disclosure_cases.csv)")
    args = parser.parse_args()
    run_demo(run_records_gate, args)


if __name__ == "__main__":
    main()
