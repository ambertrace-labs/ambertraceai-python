"""79 — Find, page through and tidy up a large account (PaginatedList, filters, reaping).

When an account holds hundreds or thousands of domains, datasets and platforms you need
to FIND things, COUNT them and CLEAN UP the abandoned ones:

  1. Every ``list()`` returns a ``PaginatedList``: a plain ``list`` of one page that also
     carries ``.total`` (the true match count), ``.limit`` and ``.offset`` -- no
     guessing from ``len``. Page with ``offset`` until ``offset + len(page) >= total``.
  2. Filter on the server: ``domains.list(q=, status=, sort=)``,
     ``platforms.list(q=, domain_id=, status=, sort=)``, ``datasets.list(domain_id=)``.
  3. Traverse containment: a platform record carries ``domain_name`` and
     ``dataset_ids`` (the datasets it was built from), so domain -> platforms -> datasets
     needs no client-side joins.
  4. Reap abandoned drafts: a ``draft`` domain with no dataset and no platform is an
     empty shell left by a run that never finished. This example lists them and, only with
     ``--apply``, deletes them in one call with ``domains.prune_drafts(older_than_days=)``
     (dry run by default).

Read-only unless --apply is passed (which reaps ALL your abandoned drafts older than
--older-than-days, not only those matching --name-prefix).

    python 79_paginate_filter_and_reap.py --name-prefix "Recurring"
"""

from __future__ import annotations

import argparse

from _common import add_common_args, print_section, run_demo

PAGE = 50


def run_tidy(api, args: argparse.Namespace) -> None:
    total = 4

    print_section(1, total, "Counting with .total")
    first = api.domains.list(limit=PAGE)
    print(f"  {len(first)} domains on this page of {first.total} "
          f"(limit={first.limit}, offset={first.offset})")

    print_section(2, total, "Paging through every domain")
    domains: list = []
    offset = 0
    while True:
        page = api.domains.list(limit=PAGE, offset=offset)
        domains.extend(page)
        offset += len(page)
        if not page or offset >= page.total:
            break
    print(f"  Collected {len(domains)} of {page.total}")

    print_section(3, total, "Filtering and traversing platforms -> datasets")
    active = api.platforms.list(status="active", sort="-updated", limit=5)
    print(f"  {active.total} active platforms; newest {len(active)}:")
    for p in active:
        print(f"    platform {p['id']} in domain {p.get('domain_name')!r} "
              f"built from datasets {p.get('dataset_ids')}")

    print_section(4, total, "Finding (and optionally reaping) abandoned draft domains")
    drafts = api.domains.list(status="draft", q=args.name_prefix or None, limit=200)
    empty = [d for d in drafts
             if not api.datasets.list(domain_id=d["id"], limit=1)
             and not api.platforms.list(domain_id=d["id"], limit=1)]
    print(f"  {len(empty)} empty draft domain(s) among {drafts.total} matching drafts")
    for d in empty:
        print(f"    {d['id']} {d['name']!r}")
    if not args.apply:
        if empty:
            print("  Dry run -- re-run with --apply to reap them.")
    else:
        reaped = api.domains.prune_drafts(older_than_days=args.older_than_days)
        print(f"  Reaped {reaped} abandoned draft domain(s) "
              f"(older than {args.older_than_days} days, none with data or a platform).")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Paginate, filter and tidy up a large account",
    )
    add_common_args(parser)
    parser.add_argument("--name-prefix", default="",
                        help="Only LIST draft domains whose name/description contains this text "
                             "(the reap itself covers every abandoned draft)")
    parser.add_argument("--older-than-days", type=int, default=30,
                        help="With --apply: only reap drafts older than this many days (default 30; 0 = all)")
    parser.add_argument("--apply", action="store_true",
                        help="Actually reap the abandoned draft domains (default: dry run)")
    args = parser.parse_args()
    run_demo(run_tidy, args)


if __name__ == "__main__":
    main()
