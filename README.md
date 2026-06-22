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

Keep the key out of source control — read it from the environment. The SDK does
this for you: set `AMBERTRACE_API_KEY` (and optionally `AMBERTRACE_BASE_URL`,
which defaults to `https://app.ambertrace.ai`) and call `from_env()`:

```python
api = AmbertraceAPI.from_env()                     # reads AMBERTRACE_API_KEY / AMBERTRACE_BASE_URL
api = AmbertraceAPI.from_env(dotenv_path=".env")   # also load a .env file (real env wins)
```

`base_url` / `api_key` are optional on the constructor too — when omitted they
fall back to those env vars (an explicit argument always wins):

```python
api = AmbertraceAPI()                               # base_url + api_key from the environment
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

# Upload data. The returned dataset exposes its fields by attribute too
# (dataset.row_count, dataset.column_count, dataset.decision_column).
dataset = api.datasets.upload(
    domain_id=domain["id"],
    file_path="contracts.csv",
)

# Build the ontology from the domain + uploaded data (async — returns a job).
# This MUST run before building a platform: without an ontology the build fails
# server-side ("Domain has no entities. Define entities before building.").
onto = api.domains.build_ontology(domain_id=domain["id"])
api.wait_for_job(onto.job_id, timeout=600)   # raises if the ontology build fails

# Build a platform (async — returns the platform and a build job). The result
# carries a normalised, stable `id` (the platform) and `job_id` (the build job),
# so you don't unwrap `build_job.job.id` / `platform.id` by hand.
result = api.platforms.create(
    domain_id=domain["id"],
    dataset_id=dataset["id"],
)
platform_id = result.id          # == result["platform"]["id"]
build_job_id = result.job_id     # == result["build_job"]["id"]

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

> Convenience methods return an `AttrDict` — a `dict` that also exposes its keys
> as attributes (`result.id`, `dataset.row_count`). Every `result["..."]`
> subscript, `.get()`, `in` test and `json.dumps()` keeps working exactly as
> before; the attribute access is additive (a key colliding with a `dict` method
> like `items` stays reachable via subscript).

## Resources

| Resource | Methods |
|----------|---------|
| `api.domains` | `list`, `create`, `get`, `update`, `delete`, `build_ontology`, `eval_config`, `set_eval_config`, `delete_eval_config`, `suggest_eval_config`, `list_templates`, `create_template`, `update_template`, `delete_template`, `feedback_stats` |
| `api.datasets` | `list`, `get`, `upload` (incl. `decision_column`), `fetch`, `fetch_multi`, `quality`, `clean`, `preview`, `delete` |
| `api.platforms` | `list`, `create`, `get`, `delete`, `status`, `query`, `suggest_rules`, `list_suggestions`, `approve_suggestion`, `reject_suggestion`, `graph` |
| `api.predictions` | `predict`, `list_configs`, `create_config`, `delete_config`, `train`, `list_predictions`, `discover_prediction_rules`, `discovered_prediction_rules`, `neurosymbolic_comparison`, `symbolic_forecast`, `residual_diagnosis` (preview) |
| `api.connectors` | `list`, `test` |
| `api.usage` | `get` |
| `api.jobs` | `get` |
| `api.api_keys` | `list`, `create`, `revoke` |
| `api.agent_policy` (preview) | `author`, `status`, `examples`, `authorize_action`, `create_session`, `step`, `get_session` |

## Agent Policy Gate (preview)

Write the rules an AI agent must obey in **plain English**; Ambertrace compiles
them to a verified policy and **proves every proposed tool-call permit/deny** —
fail-closed, with a machine-checked proof. The LLM only *proposes*; the kernel
*proves*. You author *English* and read back the admitted rules (also in English)
plus a permit/deny verdict with its proof; the compiled form stays internal.

The gate is feature-flagged server-side (`AMBERTRACE_AGENT_POLICY_GATE`) and
reachable at `api.agent_policy.*`:

| Method | What it does |
|--------|--------------|
| `author(policy_text)` | Compile an English policy into a verified gate; returns `{platform, admitted, rejected, policy_text}` |
| `status()` | The live gate: active policy, admitted controls (English), and the declared `input_fields` an action must supply |
| `examples()` | The built-in example-policy library (`[{id, domain_label, title, policy_text, try_hint}, ...]`) — ready-to-author policies |
| `authorize_action(platform_id, *, tool, args, context)` | Gate ONE proposed tool-call — permit/deny **with proof** |
| `create_session(*, platform_id, goal)` | Open a mediated session (the gate is the sole executor) for a cumulative obligation |
| `step(session_id, *, tool, args, context)` | Mediate one action in a session: gate → execute-on-permit / block-on-deny |
| `get_session(session_id)` | Fetch a session and its full mediated step trace |

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
v["decision"]       # "permit" | "deny" | a policy's own verb (e.g. "escalate"/"clear")
v["permitted"]      # True iff the verdict is WITHIN policy (non-restrictive) — the
                    #   binary execute/block reading when the decision is a domain verb
v["proof_checked"]  # True — the kernel certified the firing set

# For a CUMULATIVE control, mediate a session so the obligation is proven over the
# accumulated executed-action ledger (the harness is the sole executor):
s = api.agent_policy.create_session(platform_id=platform_id, goal="place orders")
step = api.agent_policy.step(s["id"], tool="place_order",
                             args={"quantity": 100, "unit_price": 400})
step["step"]["verdict"]["decision"], step["step"]["executed"]
```

Runnable end-to-end demos (on GitHub — the runnable examples are **not bundled in
the wheel**, so install-from-PyPI users browse them on the repo, or read the full
flow offline via `help(api.agent_policy)`):
[**Agent Policy Gate quickstart**](https://github.com/ambertrace-labs/ambertraceai-python/blob/main/examples/AGENT_POLICY_GATE_QUICKSTART.md)
(the author → status → authorize / session flow + what a 404 means),
[`examples/27_agent_policy_gate.py`](https://github.com/ambertrace-labs/ambertraceai-python/blob/main/examples/27_agent_policy_gate.py)
gates a single action (permit one, deny another, print the proof certificate), and
[`examples/25_agent_spend_budget.py`](https://github.com/ambertrace-labs/ambertraceai-python/blob/main/examples/25_agent_spend_budget.py)
mediates a session for a cumulative spend budget.

**What the proof is — and is not.** The verdict's proof certificate (`decision`,
`permitted`, `proof_checked`, `deciding_rule`, `certified_facts`, `rejected_facts`)
is an **output** the verified engine produces: it demonstrates the *result* —
which facts were certified, which rule decided, and that the firing set was
machine-checked. It does **not** ship or reveal the kernel / Lean formalisation
that produces it; you read the certificate, the engine stays internal.

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

**`author()` 404 — feature-off vs not-authorised.** A 404 from `author()` has
*two* possible meanings: (a) the feature isn't enabled (above), or (b) an org
agent-policy gate **already exists** and your credentials are not its **owner**
or an **org-admin**. The org has one gate; the first `author` creates it (you
become owner) and only the owner/an org-admin may replace it thereafter. The
refusal is a 404 by design (not a 403) so the gate's existence isn't revealed to
an unauthorised caller — it is *not* a sign the feature is unavailable. To
replace an existing org gate, author with the owner's credentials or an org-admin
key. (`status()` / `authorize_action()` / `step()` against an existing gate are
read/eval paths and do not require ownership.)

## Neurosymbolic forecasting

Train a forecasting model, then **discover explainable correction rules** from its
residuals and check — honestly — whether they earn their place against the neural
model alone.

```python
# Train a Time-Series config (target = GS10, the 10y Treasury yield)
config = api.predictions.create_config(platform_id, target_field="GS10",
                                       time_index_field="date", horizon=1,
                                       frequency="monthly", model_type="gbt")
api.predictions.train(platform_id, config["id"])

# 1) Discover correction rules — async; the SDK polls the job and returns the summary
summary = api.predictions.discover_prediction_rules(
    platform_id, prediction_config_id=config["id"])
summary["total_accepted"], summary["total_rejected"], summary["converged"]

# 2) Read the accepted rules WITH their fire-rate and backtest delta (why each earns its place)
rules = api.predictions.discovered_prediction_rules(
    platform_id, prediction_config_id=config["id"])["accepted_rules"]
for r in rules:
    print(r["name"], r["rule_type"], r["fire_rate"], r["delta"])
# Discovered rules are stored PENDING expert approval (is_active=False) — review,
# then activate with api.platforms.update_rule(...).

# 3) Symbolic forecast — a transparent number with its WHY (the driver-rules behind it)
fc = api.predictions.symbolic_forecast(platform_id, prediction_config_id=config["id"],
                                       include_fitted_series=True)
fc["forecast"], fc["why"]   # each why-entry: driver, direction, contribution, base_features

# 4) Neural vs neurosymbolic — does the symbolic layer earn its place? (async; polled)
cmp = api.predictions.neurosymbolic_comparison(platform_id, prediction_config_id=config["id"])
cmp["neural"]["r2"], cmp["neurosymbolic"]["r2"], cmp["delta"]   # delta = neurosymbolic − neural
```

`discover_prediction_rules` and `neurosymbolic_comparison` are async (HTTP 202):
by default the SDK polls the background job to completion and returns its result
— pass `wait=False` to get the raw `{job_id, poll, ...}` envelope and poll it
yourself via `api.wait_for_job(job_id)`. Discovery is a **write** operation, so it
needs a user-scoped (`at_...`) key. A runnable end-to-end demo is in
[`examples/26_neurosymbolic_bond_yield.py`](examples/26_neurosymbolic_bond_yield.py).

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

**Progress + stall detection.** `wait_for_job` takes two optional, back-compatible
hooks so you can surface progress and catch a build that hangs without
hand-rolling a retry wrapper:

```python
# Live progress on every poll:
api.wait_for_job(job_id, on_progress=lambda j: print(j.get("status"), j.get("progress")))

# Bail out if the build makes no forward progress (a change in status or
# `progress`) for 120s — even if the overall timeout hasn't elapsed:
try:
    api.wait_for_job(job_id, timeout=600, stall_timeout=120)
except TimeoutError as e:
    print("build stalled:", e)   # e.g. stuck at building_ontology progress 0
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

When a verified `platforms.query` fails closed (the engine could not certify a
decision), the error carries machine-readable diagnostics so you don't have to
string-parse the prose message:

```python
try:
    api.platforms.query(platform_id, query="...")
except AmbertraceError as e:
    e.missing_atoms    # atoms a decision rule needed but were neither supplied nor derived
    e.deciding_rule    # the rule that stalled, if named
    e.rejected_facts   # facts the engine rejected
    e.stalled_stage    # where the chain stopped (e.g. "decision")
```

Each defaults to `[]` / `None` when the deployment doesn't supply it (back-compatible).
This brings the query failure path to parity with
`agent_policy.authorize_action()`, which already returns structured `rejected_facts`
/ `deciding_rule`.

## API Documentation

Full API reference: [app.ambertrace.ai/openapi/redoc](https://app.ambertrace.ai/openapi/redoc)

## Changelog

### 0.17.0

- **Developer-experience ergonomics (no breaking changes).**
  - **`AmbertraceAPI.from_env()`** (and env defaults on the constructor): reads
    `AMBERTRACE_API_KEY` / `AMBERTRACE_BASE_URL` (base URL defaults to
    `https://app.ambertrace.ai`), with optional `.env` loading via
    `from_env(dotenv_path=...)` — no per-project auth boilerplate. An explicit
    argument always wins over the environment.
  - **Consistent envelopes.** `platforms.create` and `domains.build_ontology`
    return an `AttrDict` stamped with a normalised, stable `id` / `job_id`
    regardless of the underlying shape (`platform.id`, `build_job.job.id`, ...),
    so callers no longer hand-roll multi-shape unwrapping. The original keys are
    preserved.
  - **Typed dataset returns.** `datasets.upload` / `get` / `list` return an
    `AttrDict` exposing the documented `DatasetOut` fields (`row_count`,
    `column_count`, `decision_column`, ...) by attribute as well as subscript —
    discoverable without grepping SDK source. `AttrDict` is a `dict` subclass, so
    every existing subscript / `.get()` / `in` / `json.dumps()` is unchanged.
  - **Build-stall detection in `wait_for_job`.** New optional `on_progress`
    callback (invoked with the job dict each poll) and `stall_timeout` (raise
    `TimeoutError` on no forward progress — a change in `status` or `progress` —
    for N seconds), so a hung build is caught without a hand-rolled retry wrapper.
    The existing two-arg signature is unchanged.
  - **Structured fail-closed query errors.** A verified `platforms.query` that
    can't certify now surfaces `missing_atoms`, `deciding_rule`, `rejected_facts`
    and `stalled_stage` on `AmbertraceError` (read off the error body; default
    `[]` / `None` when absent) — parity with `agent_policy.authorize_action`.
  - **`decision_column` docstring.** `datasets.upload(..., decision_column=...)`
    now documents that naming a column flips the build from features-only to
    **label-supervised** (verdict generation grounded against the labelled
    outcomes).

### 0.16.0

- **Agent Policy Gate — documented + exampled.** The `api.agent_policy` resource
  (author an English governance policy, then prove every proposed agent action
  permit/deny against it — fail-closed, with a machine-checked proof) is now fully
  surfaced in the README (the [Agent Policy Gate](#agent-policy-gate-preview)
  section, the method table, and the obligation-class authoring contract) and in a
  new single-action worked example, `examples/27_agent_policy_gate.py` — author a
  per-action policy, gate a PERMIT case and a DENY case, and print the verdict's
  proof certificate (`decision`, `permitted`, `proof_checked`, `deciding_rule`,
  `certified_facts`, `rejected_facts`, `denied_reason`). The proof certificate is
  an **output** demonstrating the result; it does not reveal the kernel/Lean
  engine that produces it. The gate is a preview capability (feature-flagged
  server-side; its endpoints return `AmbertraceError` (404) when not enabled).
  No client API changed — `AgentPolicyResource` already shipped.

### 0.15.0

- **Multi-source connector fetch + decision-column upload.**
  `api.datasets.fetch_multi(domain_id=..., sources=[...], join_on="date", ...)`
  fetches from two or more connectors and merges them into ONE date-aligned panel
  (each value column namespaced by connector type), with optional `frequency` /
  `aggregation` resampling so mixed-cadence sources land on a common grid.
  `api.datasets.upload(...)` now accepts `decision_column=` to declare the
  dataset's decision/label column at upload time.

### 0.11.2

- **Per-period neurosymbolic-comparison series (for charting).**
  `neurosymbolic_comparison` now accepts `include_series=True` — the completed job
  result then carries a `series` list of the per-period neural-vs-neurosymbolic
  head-to-head over the SAME held-out backtest points the aggregate metrics are
  computed from, so the comparison can be charted OVER TIME. Each entry is
  `{index, time?, actual, neural, neurosymbolic, rule_fired}` (`rule_fired` marks
  the periods where applying the rules changed the prediction). The series
  reconciles with the aggregate metrics and honours `include_pending`. Omitted by
  default (additive / back-compatible); timeseries configs only.

### 0.11.1

- **Sound neurosymbolic loop + `include_pending` preview.** `neurosymbolic_comparison`
  now accepts `include_pending=True` — a read-only "what-if" that applies the
  accepted-but-pending discovered rules before the human approval gate (`mode`
  switches to `preview_pending`, with `n_pending_rules`); default scores active
  rules only. Server-side, rule discovery is corrected to score candidates in the
  same space they're applied (greedy forward selection through the live evaluator),
  so an accepted rule set never degrades the backtest, and discovery now runs on
  `ingested`-status datasets (previously it silently returned no rules). Cleaner
  generated module names throughout (explicit `operationId`s on every route).

### 0.11.0

- **Neurosymbolic rule discovery + neural-vs-neurosymbolic comparison.** New
  `api.predictions` methods: `discover_prediction_rules` (async — analyse a
  trained model's residuals, propose corrective adjustment/constraint rules, and
  A/B-test each against the expanding-window backtest; accepted rules are stored
  pending expert approval), `discovered_prediction_rules` (read the accepted rules
  with each rule's `fire_rate` and backtest `delta`), and
  `neurosymbolic_comparison` (async — head-to-head neural vs neurosymbolic R²/RMSE
  so you can see whether the symbolic layer earns its place). The two async
  methods poll the background job by default; pass `wait=False` for the raw 202
  envelope. New headline example `examples/26_neurosymbolic_bond_yield.py` walks
  the full 10y-Treasury-yield flow end to end.

### 0.10.2

- **`symbolic_forecast` `why` contract — enriched (non-breaking superset).** `why`
  now surfaces the **full set of materially-contributing accepted drivers** the
  model induced and accepted on the holdout — not only the drivers firing on the
  most-recent row. So `why` is informative even when nothing fires on the latest
  row (the case where it used to come back `[]`). Each entry carries
  `fired_on_latest_row` (is this driver active now?), `base_features` (the
  human-named source feature(s) behind an engineered antecedent), and
  `standalone_holdout_skill` (per-driver data-fit evidence); a new top-level
  `max_standalone_holdout_skill` reports the strongest single driver's skill.
  `accepted_drivers` is now an **alias of `why`** (same content, one source of
  truth). This is a **non-breaking superset**: the `forecast` value/interval,
  `baseline`, and `skill_vs_persistence` are unchanged — consumers reading `why`
  simply get the full driver set instead of the fired-only subset. Read the
  enriched `why` to explain a forecast even off the latest row.

### 0.10.1

- Trim-forward release: IP-redacted docstrings for the public SDK.
