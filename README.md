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
| `api.platforms` | `list`, `create`, `get`, `delete`, `update`, `status`, `query`, `suggest_rules`, `list_suggestions`, `approve_suggestion`, `reject_suggestion`, `graph`, `list_rules`, `create_rule`, `update_rule`, `delete_rule`, `capture_drift_baseline`, `check_drift` |
| `api.predictions` | `predict`, `list_configs`, `create_config`, `delete_config`, `train`, `list_predictions` |
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

## Verified Profile

Platforms can be built with the verified profile for proof-carrying queries:

```python
result = api.platforms.create(
    domain_id=domain["id"],
    dataset_id=dataset["id"],
    verified_profile=True,
    verified_min_confidence=0.85,
    invariant_manifest=[
        {"name": "no_unconditional_delete", "kind": "forbid",
         "target": "permit_delete", "assumed_absent": ["permit_delete"]},
    ],
)

# Query — response includes proof certificate
answer = api.platforms.query(platform_id, query="What permissions does alice have?")
print(answer["proof_checked"])   # True
print(answer["proof_summary"])   # Human-readable certificate

# Drift monitoring
api.platforms.capture_drift_baseline(platform_id)
drift = api.platforms.check_drift(platform_id)
print(drift["drift_detected"])   # False
```

## Rules CRUD

Manage symbolic rules on a platform:

```python
rules = api.platforms.list_rules(platform_id)

rule = api.platforms.create_rule(
    platform_id,
    name="viewer_read_only",
    condition={"field": "role", "operator": "==", "value": "viewer"},
    action={"type": "derive", "value": "read_only"},
)

api.platforms.update_rule(platform_id, rule["id"], description="Updated desc")
api.platforms.delete_rule(platform_id, rule["id"])
```

## Job Polling

Long-running operations (platform builds, data cleaning, training) return a `job_id`. Use `wait_for_job` to poll:

```python
job = api.wait_for_job(job_id, timeout=300, poll_interval=5)
if job["status"] == "error":
    print(f"Failed: {job.get('error_message')}")
```

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
