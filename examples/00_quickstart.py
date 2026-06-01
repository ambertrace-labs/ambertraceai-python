"""00 — Quickstart: connect and read.

The smallest possible program: build a client and list what's already on your
account. Read-only — creates nothing. Run this first to confirm your key works.

    python 00_quickstart.py
"""

from _common import banner, get_client, step


def main() -> None:
    api = get_client()
    banner("Quickstart — connectivity check")

    domains = api.domains.list()
    step(f"You have {len(domains)} domain(s).")
    for d in domains[:5]:
        print(f"      #{d['id']}  {d['name']}")

    datasets = api.datasets.list()
    step(f"You have {len(datasets)} dataset(s).")

    platforms = api.platforms.list()
    step(f"You have {len(platforms)} platform(s).")
    for p in platforms[:5]:
        print(f"      #{p['id']}  {p.get('name', '(unnamed)')}  [{p.get('status', '?')}]")

    print("\n✓ Connected to Ambertrace successfully.")


if __name__ == "__main__":
    main()
