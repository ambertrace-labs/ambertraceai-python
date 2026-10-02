# AGENTS.md -- Ambertrace API orientation for LLMs and autonomous agents

One-page entry-point for programmatic consumers of the Ambertrace API.
Human-readable docs: <https://app.ambertrace.ai/docs>

## Base URL and spec

| Resource | URL |
|----------|-----|
| Base URL | `https://app.ambertrace.ai` |
| OpenAPI spec (JSON) | `https://app.ambertrace.ai/api/v1/openapi.json` |
| Interactive docs (ReDoc) | `https://app.ambertrace.ai/docs` |

All endpoints are under `/api/v1/`.

## Authentication

Every request (except `/api/v1/health`, `/api/v1/openapi.json`, and `/docs`)
requires a Bearer token.

```
Authorization: Bearer at_...
```

Obtain a token in one of two ways:

1. **API key** (recommended for agents): create one from the dashboard
   (Settings > API Access) or via `POST /api/v1/api-keys`. Keys are scoped
   (org-wide or platform-specific) and start with `at_`.
2. **Session login**: `POST /api/v1/auth/login` with `{email, password}` --
   returns a JWT in a cookie. Suitable for interactive use, not agents.

SDK shortcut:

```python
from ambertraceai import AmbertraceAPI
api = AmbertraceAPI.from_env()  # reads AMBERTRACE_API_KEY + AMBERTRACE_BASE_URL
```

## Golden-path workflow

The canonical sequence to go from nothing to a verified, queryable AI platform:

1. **Create a domain** -- `POST /api/v1/domains`
   Define the area of expertise (entities, relationships, decision vocabulary).

2. **Upload data** -- `POST /api/v1/datasets/upload` (multipart CSV)
   Attach a dataset to the domain. The platform maps columns to domain entities.

3. **Build ontology** -- `POST /api/v1/domains/{id}/build-ontology`
   Generate the neurosymbolic rule set from the domain definition and data.
   Returns **202** (async job -- see "Async jobs" below).

4. **Create platform** -- `POST /api/v1/platforms`
   Build a queryable neurosymbolic platform from the domain + data + ontology.
   Set `verified_profile: true` for proof-carrying decisions.
   Returns **202** (async job).

5. **Query** -- `POST /api/v1/platforms/{id}/query`
   Submit facts, get a decision with full explainability (proof chain,
   deciding rules, rejected facts, Amber Report).

See `examples/00_quickstart.py` through `examples/02_platform_lifecycle.py`
for runnable code.

**Universal claims (certified search)** -- `POST /api/v1/platforms/{id}/verify-property`
(SDK: `platforms.verify_property`). Where `query` certifies one input, this certifies a
mechanism for EVERY case in a finite space you declare: `result` is `HOLDS`
(`certified: "exhaustive"`), `VIOLATED` (a re-certified `witness`) or `ABSTAIN`
(space above your `bound`/the platform ceiling -- never a pass). Branch on `result`
and `proof_checked`. See `examples/69_verify_property_strategy_proof.py`.

## Async jobs

Long-running operations (ontology build, platform build, predictions) return
**202 Accepted** with a job ID:

```json
{"data": {"job_id": "...", "status": "pending"}}
```

Poll `GET /api/v1/jobs/{id}` every 5 seconds until `status` is
`"completed"` or `"failed"`. The SDK's convenience methods handle polling
automatically.

## Response envelope

All responses use a consistent envelope:

- **Success**: `{"data": {...}}` with status 200/201/202.
- **Error**: `{"error": {"code": "...", "message": "..."}}` with the
  appropriate HTTP status (400, 401, 403, 404, 409, 422, 500, 503).

## Error contract -- machine-readable self-correction

When a query or action is rejected, the error body carries structured
diagnostics designed for programmatic retry:

| Field | Type | Meaning |
|-------|------|---------|
| `rejected_facts` | `list[{field, value, reasons}]` | Which input facts were rejected and why |
| `missing_inputs` | `list[str]` | Required fields the caller did not supply |
| `deciding_rule` | `object` | The rule that drove the deny/reject decision |
| `stalled_stage` | `string` | Pipeline stage that could not complete |
| `unmappable_fields` | `list[str]` | Uploaded columns that could not be mapped to domain entities |

These fields appear on both the 503 fail-closed error and the 200
`explanation.rejected_facts` for partial rejections. The SDK surfaces them
as attributes on `AmbertraceError` (e.g. `err.rejected_facts`,
`err.stalled_stage`).

**Self-correction pattern**: on a 422/503, read `rejected_facts` or
`missing_inputs`, fix the input, and retry -- do not parse the `message`
string.

## Runnable examples

The SDK ships numbered examples (`examples/00_quickstart.py` through
`examples/47_forecast_regime_eval_config.py`) covering every major capability.
Each is self-contained and runnable with `python examples/NN_name.py` after
setting `AMBERTRACE_API_KEY` and `AMBERTRACE_BASE_URL`.

Key examples by capability:

| Capability | Example |
|------------|---------|
| End-to-end quickstart | `00_quickstart.py` |
| Verified / proof-carrying platform | `10_verified_profile.py` |
| Agent policy gate | `27_agent_policy_gate.py` |
| Multi-class classifier | `38_symmetric_multiclass_classifier.py` |
| Time-series forecast | `16_timeseries_forecast.py`, `06_predictions.py` |
| Public-data connectors | `44_public_data_connectors.py` |
| Decision logic map | `43_decision_logic_map.py` |

## What is NOT in the API

The following capabilities are console-/IdP-driven by design. Do not attempt
to automate them via the REST API:

- **SSO (SAML/OIDC) configuration** -- configured by an org admin in the
  dashboard or by the IdP. The API exposes read-only SSO status, not setup.
- **SCIM provisioning** -- driven by the IdP, not by API callers.
- **MFA enrollment/management** -- user-interactive flow in the dashboard.
- **Billing and subscription changes** -- operator-only, not self-service
  via the API.

## Links

- [Capability index](README.md#capability-index--what-can-i-do-and-which-method-produces-it) -- authoritative map from capability to SDK method
- [Agent Policy Gate quickstart](examples/AGENT_POLICY_GATE_QUICKSTART.md)
- [PyPI package](https://pypi.org/project/ambertraceai/)
