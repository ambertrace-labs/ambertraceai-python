"""52 — Policy Gallery (browse the built-in example library, then author one).

The Agent Policy Gate ships a curated library of ready-to-author English policies —
one per common governance pattern (spend budgets, rate limits, tool allow-lists, PII
egress, and so on). This demo BROWSES that gallery and then AUTHORS one of its
entries programmatically: it picks a policy from the library, prints its full English
text, and compiles it into a verified gate, reading back the admitted rules and the
declared input fields an action must supply. No other example surfaces this library.

Every entry's ``policy_text`` is a complete English policy you can pass straight to
``author()`` — so the gallery doubles as a discoverable starting point: pick the one
closest to your need, read it, author it, then edit the English and re-author. This
is a verified GATE, not a dataset-trained platform — the policy is authored from
English, so there is no domain/data upload step.

What it shows:

  1. List the built-in example-policy library and print, for each entry, its id,
     domain label, title, try-hint, and a one-line snippet of the policy text
  2. Pick one entry (the FIRST by default, or --pick <id> to choose by id) and print
     its full English policy_text
  3. Author the chosen policy and read back the platform id, the admitted verified
     rule(s), and the declared input fields an action must supply

The Agent Policy Gate is a preview capability; when it is not enabled on your
deployment the endpoints return 404, which this demo reports cleanly and skips. An
empty library (no example policies provisioned) is also reported.

Creates resources on your account. Run with --help for options.

    python 52_policy_gallery.py
    python 52_policy_gallery.py --pick spend_budget   # author a specific entry by id
"""

from __future__ import annotations

import argparse

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _print_inputs(status: dict) -> None:
    inputs = status.get("input_fields") or []
    if not inputs:
        # No declared inputs at all (e.g. a policy with no per-action operands).
        print("  No declared input fields: the gate still constrains whatever the "
              "action proposes.")
        return
    # A cumulative-exposure policy reads its operands (quantity / unit_price) from
    # the LEDGER ROW each action contributes; those operand columns are surfaced as
    # input_fields, so an action supplies them as args and the gate proves the
    # obligation over the resulting ledger.
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}")


def _snippet(text: str, width: int = 100) -> str:
    """A single-line snippet of an English policy (collapse whitespace, clip)."""
    one_line = " ".join((text or "").split())
    return one_line if len(one_line) <= width else one_line[: width - 1] + "…"


def _list_gallery(api) -> list[dict] | None:
    """Return the example-policy library, or None on a 404 preview-skip."""
    try:
        return api.agent_policy.examples()
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("\n  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) — skipping.")
            return None
        raise


def _pick_entry(gallery: list[dict], pick) -> dict | None:
    """Choose the entry whose id matches --pick, or the first entry by default."""
    if pick is None:
        return gallery[0]
    target = str(pick)
    for entry in gallery:
        if str(entry.get("id")) == target:
            return entry
    print(f"\n  No example policy with id {pick!r} — available ids: "
          f"{', '.join(str(e.get('id')) for e in gallery)}")
    return None


def run_policy_gallery_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Browsing the built-in example-policy library")
    gallery = _list_gallery(api)
    if gallery is None:
        return
    if not gallery:
        print("  The example-policy library is empty on this deployment — nothing "
              "to author.")
        return

    print(f"  {len(gallery)} example polic(ies) available:\n")
    for entry in gallery:
        print(f"  [{entry.get('id')}] {entry.get('title')}  "
              f"({entry.get('domain_label')})")
        if entry.get("try_hint"):
            print(f"      try: {entry.get('try_hint')}")
        print(f"      policy: {_snippet(entry.get('policy_text', ''))}")
        print()

    print_section(2, 3, "Picking one entry and reading its full policy text")
    chosen = _pick_entry(gallery, args.pick)
    if chosen is None:
        return
    print(f"  Selected [{chosen.get('id')}] {chosen.get('title')} "
          f"({chosen.get('domain_label')}).")
    print(f"\n  POLICY:\n    {chosen.get('policy_text')}\n")

    print_section(3, 3, "Authoring the chosen policy (English in) + reading it back")
    try:
        result = api.agent_policy.author(chosen["policy_text"])
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("\n  The Agent Policy Gate is not enabled — skipping author step.")
            return
        raise
    platform = result.get("platform") or {}
    print(f"  Authored verified policy -> platform {platform.get('id')} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)
    _print_inputs(api.agent_policy.status())

    print("\nDone. The admitted rules above are the authoritative plain-English "
          "read-back of what the chosen gallery policy MEANS — author one, review "
          "it, then edit the English and re-author to tailor it to your domain.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Policy Gallery — browse AmberTrace AI's built-in example-policy "
                    "library and author one into a verified agent-policy gate",
    )
    add_common_args(parser)
    parser.add_argument(
        "--pick", default=None,
        help="Author the example policy with this id (default: the first entry). "
             "Run once with no --pick to see the available ids.",
    )
    args = parser.parse_args()
    run_demo(run_policy_gallery_demo, args)


if __name__ == "__main__":
    main()
