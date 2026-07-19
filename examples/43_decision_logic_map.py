"""43 -- Decision-logic map: inspect a platform's rule-dependency DAG.

After building a neurosymbolic platform, call ``GET /api/v1/platforms/{id}/
decision-logic-map`` to retrieve the decision-logic DAG.  The response contains:

  * **nodes** -- classifiers (derive rules), verdicts (decision conclusions), and
    declared outcomes, each with a ``fire_rate`` (fraction of sample rows the rule
    fires on), ``reachable`` flag, and ``connected`` status.
  * **edges** -- dependency links (``verdict -> outcome``) showing which verdict
    certifies which declared outcome.
  * **unreachable_outcomes** -- declared decision classes that no firing chain
    reaches, with a machine-readable ``reason`` and a human-readable ``detail``
    explaining why (no verdict rule, all dangling, all dead on sample data).

Use-cases:
  * **Domain authoring feedback** -- identify dead rules (fire_rate == 0) and
    unreachable outcomes so authors can fix their domain before going live.
  * **Audit / compliance** -- prove every declared decision class is reachable
    by a connected, firing verdict chain.
  * **Visualization** -- render the DAG in a UI (nodes + edges are graph-ready).

This example fetches the map for an existing platform and prints a summary.
"""

from _common import get_client

api = get_client()

# -- Replace with a real platform ID from your organisation ----------------
PLATFORM_ID = 1

resp = api.get(f"/api/v1/platforms/{PLATFORM_ID}/decision-logic-map")

if resp.status_code == 404:
    print("No decision-logic map available (platform may not have been built).")
elif resp.status_code == 200:
    data = resp.json()["data"]

    print(f"Firing evaluated: {data['firing_evaluated']}  "
          f"(sample rows: {data['n_rows']})")

    summary = data["summary"]
    print(f"\nSummary: {summary['classifier_count']} classifiers, "
          f"{summary['verdict_count']} verdicts, "
          f"{summary['declared_outcome_count']} declared outcomes, "
          f"{summary['unreachable_outcome_count']} unreachable")

    # Print nodes grouped by type
    for node_type in ("classifier", "verdict", "outcome"):
        typed_nodes = [n for n in data["nodes"] if n["type"] == node_type]
        if not typed_nodes:
            continue
        print(f"\n--- {node_type.upper()}S ---")
        for node in typed_nodes:
            status = "REACHABLE" if node["reachable"] else "UNREACHABLE"
            rate = (f"fire_rate={node['fire_rate']:.2%}"
                    if node["fire_rate"] is not None else "fire_rate=N/A")
            extra = ""
            if node.get("is_default"):
                extra = " [DEFAULT]"
            print(f"  {node['name']}: {status}, {rate}{extra}")

    # Print edges
    if data["edges"]:
        print("\n--- EDGES ---")
        for edge in data["edges"]:
            print(f"  {edge['source']} --[{edge['relation']}]--> {edge['target']}")

    # Highlight unreachable outcomes
    if data["unreachable_outcomes"]:
        print("\n--- UNREACHABLE OUTCOMES ---")
        for u in data["unreachable_outcomes"]:
            print(f"  {u['outcome']}: {u['detail']}")
            if u.get("verdict_names"):
                print(f"    Blocking verdict(s): {', '.join(u['verdict_names'])}")
else:
    print(f"Error {resp.status_code}: {resp.json()}")
