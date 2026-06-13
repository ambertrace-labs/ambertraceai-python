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

- the **ontology build** job (`type: "ontology"`, created by `domains.build_ontology`) — its `result` is the ontology; the per-pass repair self-reports live on the domain's stored ontology at `ontology.generation.conclusion_repair` / `classifier_repair`, **not** in the job result.
- the **platform build** job (`type: "build"`, the `build_job` from `platforms.create`) — its `result.generation_diagnostics` carries the build-generation payload below.

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

# Repair self-reports show what generation did to close coverage gaps.
if diag.get("conclusion_repair", {}).get("fired"):
    print("conclusion repair:", diag["conclusion_repair"]["outcome"])
```

Fields: `rule_count`, `classifier_count`, `verdict_conclusion_count`, `connected_restrictive_count` (ints); `can_decide_adversely` (bool); `decision_coverage_warnings`, `non_discriminating_rules`, `orphan_derived` (list[str]), `unbound_references` (list); `conclusion_repair` and `classifier_repair` (dicts: `fired`, `trigger`, `outcome`, `added`, …); `builder_version` (int).

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
