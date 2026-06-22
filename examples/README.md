# AmbertraceAI SDK Examples

Runnable, self-contained examples for the [`ambertraceai`](https://pypi.org/project/ambertraceai/) Python SDK.

## Setup

```bash
pip install ambertraceai

cd examples
cp .env.example .env          # then edit .env and add your API key
```

Your `.env` (gitignored) holds:

```
AMBERTRACE_API_KEY=at_your_key_here
# AMBERTRACE_BASE_URL=https://app.ambertrace.ai   # optional
```

Create a key from the dashboard at [app.ambertrace.ai](https://app.ambertrace.ai) → **Settings → API Keys**.

## The examples

Run them in order — each is independent, but they build conceptually.

| Script | What it shows | Writes data? |
|--------|---------------|--------------|
| `00_quickstart.py` | Connect and list your domains/datasets/platforms | No (read-only) |
| `01_domain_and_data.py` | Create a domain, upload a dataset, check quality, clean | Yes (self-cleans) |
| `02_platform_lifecycle.py` | Full build: domain → ontology → platform → query | Yes (self-cleans) |
| `03_connectors.py` | Discover external data-source connectors | No (read-only) |
| `04_api_keys.py` | Create / list / revoke a platform-scoped API key | Yes (self-cleans) |
| `05_rules_and_suggestions.py` | Ask a platform to suggest symbolic rules | No |
| `06_predictions.py` | Configure, train, and run a forecast | Yes (self-cleans) |
| `07_usage.py` | Report API usage (requests, tokens, budget) | No (read-only) |
| `08_fred_forecast.py` | Ingest FRED macro series → explainable forecast of the 10y yield | Yes (self-cleans) · needs `FRED_API_KEY` |
| `09_fred_analysis.py` | Ingest FRED series → explainable macro Q&A | Yes (self-cleans) · needs `FRED_API_KEY` |
| `10_verified_profile.py` | Verified platform: proof-carrying queries, rules CRUD, drift monitoring | Yes (self-cleans) |

### Domain demos

End-to-end examples that create a domain, upload sample data, build a platform
with symbolic rules, and run queries that produce **Amber Reports** — the
platform's headline explainability feature. Each demo covers a different
regulated industry. Sample data CSVs live in `data/`.

| Script | Domain | Sample data |
|--------|--------|-------------|
| `11_fraud_detection.py` | Insurance claims fraud | `data/insurance_claims.csv` |
| `12_clinical_safety.py` | Clinical prescribing safety | `data/clinical_prescriptions.csv` |
| `13_loan_assessment.py` | Loan approval (fair lending) | `data/loan_applications.csv` |
| `14_recruitment_compliance.py` | HR recruitment (equality) | `data/recruitment_applications.csv` |
| `15_environmental_compliance.py` | Environmental regulatory | `data/environmental_monitoring.csv` |
| `16_timeseries_forecast.py` | Environmental forecasting | `data/environmental_monitoring.csv` |
| `17_rule_coverage.py` | Vehicle inspection (rule regression) | `data/vehicle_inspections.csv` |

### Verified profile demos

Proof-carrying decision domains that use the verified profile — every answer
arrives with a machine-checked proof, or is fail-safe refused when it can't be
certified. Supply structured facts and read the certified verdict from the
symbolic trace.

| Script | Domain | Sample data |
|--------|--------|-------------|
| `18_access_governance.py` | Access governance PDP (permit/deny) | `data/access_requests.csv` |
| `19_air_track_triage.py` | Air track C2 triage (escalate/monitor/clear) | `data/air_tracks.csv` |
| `24_air_track_isr_hispec.py` | High-spec ISR air track triage (ASTERIX/MISB schema) | `data/air_tracks_hispec.csv` |

### Agent Policy Gate demos (preview)

Author a governance policy in **plain English**, then **prove every proposed
agent action permit/deny** against it — fail-closed, with a machine-checked proof.
No dataset upload: the policy is authored from English. The proof certificate is
an OUTPUT (which facts were certified, which rule decided, machine-checked) — it
does not reveal the kernel/Lean engine that produces it. Preview capability:
feature-flagged server-side; the endpoints return 404 when not enabled (each demo
reports that cleanly and skips).

**New here? Start with the [Agent Policy Gate quickstart](AGENT_POLICY_GATE_QUICKSTART.md)** —
the author → status → authorize / session flow, key authority (what a 404 means), and
the four things to get right — then run the demos below.

For a software-supply-chain walkthrough, `28_agent_policy_gate_cicd.py` gates a
CI/CD deploy agent. Note that genuine **temporal / ordering** obligations (release
only inside the approved change window; review-before-merge) are a roadmap item:
today the gate proves them as **caller-supplied booleans** (`within_change_window`,
`code_review_approved`) rather than reasoning about time/order itself.

**Branch on `verdict["outcome"]`, not just `permitted`.** Each verdict reports one
of `permit` | `deny` | `indeterminate` | `unavailable`. `indeterminate` means the
gate needed a declared input it was not given (see `verdict["missing_inputs"]`): it
keeps `permitted=False` and `proof_checked=False`, but it is **not** a policy
denial — supply the missing field(s) and retry rather than giving up. Only `deny`
(with `proof_checked=True`) is a proven violation; only `permit` should execute.

| Script | What it shows |
|--------|---------------|
| `27_agent_policy_gate.py` | Single-action gate — author a per-action policy, permit one action and deny another, print the proof certificate |
| `28_agent_policy_gate_cicd.py` | CI/CD deploy gate — a software-supply-chain policy (enum allowlist + boolean preconditions + canary-rollout cap); gates a compliant deploy (permit) and several single-fact-flipped cases (deny). Temporal/ordering rules (change window, review-before-merge) are enforced as caller-supplied booleans — native temporal/happens-before is a roadmap item |
| `25_agent_spend_budget.py` | Cumulative spend budget — mediate a session so the obligation is proven over the accumulated ledger (with a `--band` interval variant) |

### Forecasting demos

Time-series and scenario forecasting via the prediction API. Create a domain,
ingest data (from CSV or a built-in connector), train a model, and run
what-if scenarios.

| Script | Domain | Data source |
|--------|--------|-------------|
| `20_bond_yield_forecast.py` | US 10y Treasury yield (macro) | `data/fred_economic_data.csv` or FRED connector (`FRED_API_KEY`) |
| `21_bitcoin_macro_forecast.py` | Bitcoin (BTC) — explainable macro-panel forecast; the system picks which crypto + macro drivers explain BTC | `data/btc_macro_panel.csv` (bundled snapshot) or live `coinbase` + `fred` connectors (`--refresh`, `FRED_API_KEY`) |
| `22_sp500_macro_forecast.py` | S&P 500 — explainable macro forecast; the system picks which macro drivers move the index | FRED connector, **live-fetch only** (`FRED_API_KEY`); S&P 500 data is not redistributable so none is bundled |
| `26_neurosymbolic_bond_yield.py` | US 10y Treasury yield — **full neurosymbolic flow** (train → discover correction rules → symbolic WHY → neural-vs-neurosymbolic comparison) | `data/fred_economic_data.csv` or FRED connector (`FRED_API_KEY`) |

`26_neurosymbolic_bond_yield.py` is the headline forecasting walkthrough: it
trains a model, **discovers explainable correction rules** from its residuals
(each printed with its fire-rate and backtest delta), reads a transparent
**symbolic forecast with its WHY**, and ends with the honest **neural vs
neurosymbolic** R²/RMSE comparison — so you can see whether the symbolic layer
earns its place. Needs a user-scoped key (`at_...`): discovery is a write
operation.

Domain demos support `--standard` (skip verified profile) and `--tau` (confidence
threshold) flags. They create resources on your account but do not self-clean —
delete via the dashboard or API when done.

```bash
python 11_fraud_detection.py
python 12_clinical_safety.py --standard
python 18_access_governance.py
python 20_bond_yield_forecast.py
python 21_bitcoin_macro_forecast.py -v
```

### Connectors and bring-your-own-key

`api.connectors.list()` shows available data sources. Ingest from one with
`api.datasets.fetch(domain_id=..., connector_type=..., config={...})`:

- `fred` / `fred_sentiment` — economic data; **bring your own** free FRED key as `config["api_key"]`.
- `yahoo` — stock/ETF close prices (`config={"symbols": ["AAPL","SPY"]}`), no key.
- `coinbase` — crypto close prices (`config={"product_ids": ["BTC-USD"]}`), no key.
- `rest` — any JSON/CSV endpoint (`config={"url": ..., "headers": {...}}`); bring your own auth.

Connectors that hit a credentialed provider always take the key in `config` — the platform never uses a shared key on your behalf.

```bash
python 00_quickstart.py
python 02_platform_lifecycle.py
```

Examples that create resources delete what they create (the platform lifecycle
deletes the platform with `api.platforms.delete()`, then its dataset and domain).

> Running write examples against the hosted platform creates real resources on
> your account and may count toward usage. The lifecycle examples clean up after
> themselves.
