# AmbertraceAI Python SDK

Python client for the [Ambertrace](https://ambertrace.ai) neurosymbolic AI platform API.

## Install

```bash
pip install ambertraceai
```

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

# Build a platform (async — returns a job)
result = api.platforms.create(
    domain_id=domain["id"],
    dataset_id=dataset["id"],
)

# Wait for the build to finish
job = api.wait_for_job(result["job_id"], timeout=600)

# Query the platform
answer = api.platforms.query(
    platform_id=result["platform_id"],
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
| `api.jobs` | `get` |

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
