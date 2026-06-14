# AmbertraceAI Python SDK

Python client for the [Ambertrace](https://ambertrace.ai) neurosymbolic AI platform API.

## Install

```bash
pip install ambertraceai
```

## Authentication

The SDK authenticates with an Ambertrace API key (prefix `at_...`). Create one from the
dashboard at [app.ambertrace.ai](https://app.ambertrace.ai) → **Settings → API Keys**, then
pass it to the client:

```python
from ambertraceai import AmbertraceAPI

api = AmbertraceAPI(base_url="https://app.ambertrace.ai", api_key="at_...")
```

Keep the key out of source control — read it from an environment variable in real code:

```python
import os
api = AmbertraceAPI(base_url="https://app.ambertrace.ai", api_key=os.environ["AMBERTRACE_API_KEY"])
```

See [Agent Keys](#agent-keys) for the user- vs. platform-scoped key model.

## Quick Start

```python
from ambertraceai import AmbertraceAPI

api = AmbertraceAPI(
    base_url="https://app.ambertrace.ai",
    api_key="at_...",
)

# Create a domain
domain = api.domains.create(
    name="Legal Contracts",
    description="Contract analysis for risk and compliance",
)

# Upload data
dataset = api.datasets.upload(
    domain_id=domain["id"],
    file_path="contracts.csv",
)

# Build a platform (async — returns the platform and a build job)
result = api.platforms.create(
    domain_id=domain["id"],
    dataset_id=dataset["id"],
)
platform_id = result["platform"]["id"]
build_job_id = result["build_job"]["id"]

# Wait for the build to finish
job = api.wait_for_job(build_job_id, timeout=600)

# Query the platform
answer = api.platforms.query(
    platform_id=platform_id,
    query="What are the highest-risk clauses?",
)
print(answer["answer"])
print(answer["explanation"])
```

## Resources

| Resource | Methods |
|----------|---------|
| `api.domains` | `list`, `create`, `get`, `update`, `delete`, `build_ontology`, `eval_config`, `set_eval_config`, `delete_eval_config`, `suggest_eval_config`, `list_templates`, `create_template`, `update_template`, `delete_template`, `feedback_stats` |
| `api.datasets` | `list`, `get`, `upload`, `fetch`, `quality`, `clean`, `preview`, `delete` |
| `api.platforms` | `list`, `create`, `get`, `delete`, `status`, `query`, `suggest_rules`, `list_suggestions`, `approve_suggestion`, `reject_suggestion`, `graph` |
| `api.predictions` | `predict`, `list_configs`, `create_config`, `delete_config`, `train`, `list_predictions`, `symbolic_forecast`, `residual_diagnosis` (preview) |
| `api.connectors` | `list`, `test` |
| `api.usage` | `get` |
| `api.jobs` | `get` |
| `api.api_keys` | `list`, `create`, `revoke` |
| `api.agent_policy` (preview) | `author`, `status`, `examples`, `authorize_action`, `create_session`, `step`, `get_session` |

## Agent Policy Gate (preview)

Write the rules an AI agent must obey in **plain English**; Ambertrace compiles
them to a verified policy and **proves every proposed tool-call permit/deny** —
fail-closed, with a machine-checked proof. You author *English* and read back the
admitted rules (also in English) plus a permit/deny verdict with its proof; the
compiled form stays internal.

```python
# 1. Author the policy in English
result = api.agent_policy.author(
    "An autonomous procurement agent may place purchase orders. Each order is "
    "recorded as a row in a purchase_orders ledger with a quantity column and a "
    "unit_price column. The cumulative spend — the sum of quantity times "
    "unit_price across every row — must stay at or below 100000. Permit a "
    "purchase order only when the resulting cumulative spend stays within budget."
)
platform_id = result["platform"]["id"]
result["admitted"]   # the admitted rules, described in plain English — review these
result["rejected"]   # anything outside the verified fragment, with a reason (never silently dropped)

# 2. See exactly which facts an action must supply
api.agent_policy.status()["input_fields"]   # e.g. quantity (int), unit_price (float)

# 3. Gate one action — permit/deny WITH PROOF
v = api.agent_policy.authorize_action(platform_id, tool="place_order",
                                      args={"quantity": 100, "unit_price": 400})
v["decision"]       # "permit" | "deny" | a policy's own verb
v["proof_checked"]  # True — the kernel certified the firing set

# For a CUMULATIVE control, mediate a session so the obligation is proven over the
# accumulated executed-action ledger (the harness is the sole executor):
s = api.agent_policy.create_session(platform_id=platform_id, goal="place orders")
step = api.agent_policy.step(s["id"], tool="place_order",
                             args={"quantity": 100, "unit_price": 400})
step["step"]["verdict"]["decision"], step["step"]["executed"]
```

A runnable end-to-end demo is in [`examples/25_agent_spend_budget.py`](examples/25_agent_spend_budget.py).

### Obligation classes — the English-in authoring contract

Every policy is a set of requirements an action must satisfy. Each requirement is
one of the classes below; author it in English and the compiler admits it as a
verified obligation (anything outside these classes is **rejected-and-surfaced**
in `result["rejected"]`, never silently approximated). Always confirm a
requirement landed as you intended by reading `result["admitted"]` and by testing
a within-limit action (expect permit) and a breaching action (expect deny).

| Class | What it expresses | Example English that compiles to it |
|-------|-------------------|-------------------------------------|
| **Per-action condition** | A check on the proposed action's own fields | "Only allow actions of type triage, schedule, or refer." / "Block any actuator command with pressure outside 2 to 8 bar." / "Require mfa_passed for privileged requests." |
| **Cumulative count / sum limit** | A cap on a running `count` or `sum` over a declared ledger of prior actions (only count/sum — never average/min/max) | "Each order writes a row to an order_log with a quantity column. The total quantity summed across all rows must stay at or below 1000." / "No more than 3 actions of this kind may be executed." |
| **Cumulative exposure** | A cap on the running value `Σ qty × price` over a declared ledger; the limit is a numeric constant | "Each order writes a row to an open_positions ledger with a quantity column and a price column. The cumulative exposure — the sum of quantity times price across every row — must stay at or below 100000." |
| **Interval / band binding** | An exposure cap proven for **every** value of one as-yet-unknown factor confined to a closed interval `[lo, hi]` (e.g. a fill price known only to lie in a band) | "For a proposed order whose fill price is not yet known but is guaranteed to be between 100 and 500, the cumulative exposure must stay at or below 100000 for every possible fill price in that range." |

The cumulative / exposure / band classes operate over a **ledger** (a named
relation of prior actions): name the ledger and its numeric column(s) in your
policy, then mediate a session (`create_session` + `step`) so the gate proves the
obligation over the resulting history. Browse `api.agent_policy.examples()` for
more ready-to-author policies across domains (healthcare triage, grid dispatch,
automation safety, access control, supply-chain).

**Availability.** The Agent Policy Gate is a preview capability; its endpoints
raise `AmbertraceError` (404) when not enabled on your deployment. The cumulative
/ exposure / band classes additionally require the platform's numeric obligation
checker to be enabled.

## Connectors

Connectors pull data from external providers. List what's available, optionally test a
config, then ingest it as a dataset linked to a domain:

```python
api.connectors.list()   # discover connectors + their required config fields

# Stocks/ETFs and crypto are keyless:
api.datasets.fetch(domain_id=1, connector_type="yahoo",
                   config={"symbols": ["AAPL", "SPY"], "range": "2y"})
api.datasets.fetch(domain_id=1, connector_type="coinbase",
                   config={"product_ids": ["BTC-USD", "ETH-USD"]})

# FRED needs your own free key (https://fred.stlouisfed.org):
api.datasets.fetch(domain_id=1, connector_type="fred",
                   config={"api_key": "<your FRED key>",
                           "series_ids": ["GS10", "FEDFUNDS"], "frequency": "monthly"})

# Generic REST/CSV — bring your own auth via headers:
api.datasets.fetch(domain_id=1, connector_type="rest",
                   config={"url": "https://api.example.com/series",
                           "headers": {"Authorization": "Bearer ..."}})
```

| Connector | Config | Key? |
|-----------|--------|------|
| `yahoo` | `symbols`, `interval`, `range` | none |
| `coinbase` | `product_ids`, `granularity` | none |
| `fred` / `fred_sentiment` | `series_ids`, `frequency`, **`api_key`** | bring your own |
| `rest` | `url`, `format`, `records_path`, `headers`, `params` | bring your own (via headers) |

**Bring your own provider keys.** Connectors that hit a credentialed provider require
*your own* key, passed in `config` — Ambertrace never uses a shared key on your behalf.

## Agent Keys

AI agents authenticate with **user-scoped API keys** that give full lifecycle access (domains, datasets, platforms, rules, predictions). A human creates the key from the dashboard; the agent can then create narrower platform-scoped keys for its integrations.

```python
# Agent creates a platform-scoped key for a specific integration
platform_key = api.api_keys.create(
    scope="platform",
    platform_id=42,
    name="Slack Integration",
)

# List keys visible to this agent
keys = api.api_keys.list()

# Revoke a platform key the agent created
api.api_keys.revoke(platform_key["id"])
```

User-scoped keys cannot create other user-scoped keys (no self-replication). Chat, conversations, and billing remain human-only.

## Job Polling

Long-running operations (platform builds, data cleaning, training) return a `job_id`. Use `wait_for_job` to poll:

```python
job = api.wait_for_job(job_id, timeout=300, poll_interval=5)
if job["status"] == "error":
    print(f"Failed: {job.get('error_message')}")
```

### Two job types — poll the right one

`GET /api/v1/jobs/{id}` (and `wait_for_job`) returns two different job *types*:

- the **ontology build** job (`type: "ontology"`, created by `domains.build_ontology`) — its `result` is the ontology.
- the **platform build** job (`type: "build"`, the `build_job` from `platforms.create`) — its `result.build_quality` carries the customer-facing build-quality summary and its `result.generation_diagnostics` the decision-coverage detail below.

A consumer polling the *ontology* job will not see `generation_diagnostics` — poll the **platform build job** id instead.

### Build diagnostics

After a platform build, `job["result"]["generation_diagnostics"]` reports what rule generation produced and how the rule set behaves — the quickest way to explain why a platform reaches (or never reaches) an adverse decision:

```python
job = api.wait_for_job(build_job_id, timeout=600)
diag = job["result"].get("generation_diagnostics", {})

# verdict_conclusion_count == 0 (== `can_decide_adversely is False`) means the
# rule set classifies inputs but has no deny/block conclusion — it permits
# everything and can never refuse.
if not diag.get("can_decide_adversely", True):
    print("Platform reaches no adverse decision:")
    for w in diag.get("decision_coverage_warnings", []):
        print("  -", w)
```

Fields: `rule_count`, `classifier_count`, `verdict_conclusion_count`, `connected_restrictive_count` (ints); `can_decide_adversely` (bool); `decision_coverage_warnings`, `non_discriminating_rules`, `orphan_derived` (list[str]), `unbound_references` (list).

## Error Handling

```python
from ambertraceai import AmbertraceAPI, AmbertraceError

try:
    api.domains.get(999)
except AmbertraceError as e:
    print(e.status_code)  # 404
    print(e.code)         # "not_found"
    print(str(e))         # "Domain not found."
```

## API Documentation

Full API reference: [app.ambertrace.ai/openapi/redoc](https://app.ambertrace.ai/openapi/redoc)
