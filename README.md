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
| `api.domains` | `list`, `create`, `get`, `update`, `delete`, `build_ontology` |
| `api.datasets` | `list`, `get`, `upload`, `fetch`, `quality`, `clean`, `preview`, `delete` |
| `api.platforms` | `list`, `create`, `get`, `status`, `query`, `suggest_rules`, `list_suggestions`, `graph` |
| `api.predictions` | `predict`, `list_configs`, `create_config`, `train`, `list_predictions` |
| `api.connectors` | `list`, `test` |
| `api.jobs` | `get` |
| `api.api_keys` | `list`, `create`, `revoke` |

## Connectors

Connectors pull data from external providers (e.g. FRED, Yahoo Finance). List what's
available, then test a config before ingesting it as a dataset:

```python
connectors = api.connectors.list()

result = api.connectors.test(
    connector_type="fred",
    config={"series_id": "GDP", "api_key": "<your FRED API key>"},
)
print(result["columns"], result["rows"])
```

**Bring your own provider keys.** Connectors that hit third-party APIs require *your own*
credentials for that provider — pass them in `config`. Ambertrace does not supply
third-party API keys on your behalf.

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
