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
| `27_aml_transaction_monitoring.py` | AML / transaction monitoring (clear/review/report) | `data/aml_transactions.csv` |
| `28_medical_device_qms.py` | Medical-device QMS nonconformance triage (ISO 13485 / CAPA) | `data/device_nonconformances.csv` |
| `29_content_moderation.py` | Trust & Safety content moderation (allow/limit/remove) | `data/content_moderation.csv` |
| `30_esg_disclosure_check.py` | ESG / CSRD disclosure completeness check | `data/esg_disclosures.csv` |

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
| `31_export_control_screening.py` | Export-control / sanctions screening (permit/license_required/deny) | `data/export_screenings.csv` |
| `32_kyc_onboarding_decision.py` | KYC onboarding decision (approve/edd/reject) | `data/kyc_applications.csv` |
| `46_soc_alert_triage.py` | SOC security-alert triage (auto_close/monitor/escalate) | `data/soc_alerts.csv` |

#### Verified-profile tooling

Cross-cutting tools on a verified platform (built on the access-governance domain).

| Script | What it shows |
|--------|---------------|
| `49_evaluate_holdout.py` | Evaluation harness: replay labeled rows → accuracy + certification rate + fail-closed rate |
| `50_verified_vs_standard.py` | Same query, verified vs standard — standard answers, verified fail-closes on under-specified input |
| `51_proof_anatomy.py` | Deep-dive: unpack every part of one proof-carrying answer (proof, confidence, symbolic trace, certified/rejected facts) |
| `53_drift_monitoring.py` | Production monitoring: capture a drift baseline at approval, replay traffic, `check_drift` for behavioural drift |

### Forecasting demos

Time-series and scenario forecasting via the prediction API. Create a domain,
ingest data (from CSV or a built-in connector), train a model, and run
what-if scenarios.

| Script | Domain | Data source |
|--------|--------|-------------|
| `20_bond_yield_forecast.py` | US 10y Treasury yield (macro) | `data/fred_economic_data.csv` or FRED connector (`FRED_API_KEY`) |
| `21_bitcoin_forecast.py` | BTC-USD daily price | Coinbase connector (no key needed) |
| `22_equity_forecast.py` | SPY daily price | Yahoo Finance connector (no key needed) |
| `26_neurosymbolic_bond_yield.py` | US 10y Treasury yield — **full neurosymbolic flow** (train → discover correction rules → symbolic WHY → neural-vs-neurosymbolic comparison) | `data/fred_economic_data.csv` or FRED connector (`FRED_API_KEY`) |
| `33_energy_demand_forecast.py` | Daily electricity demand — **full neurosymbolic flow** (self-contained, weather-driven) | `data/energy_demand.csv` |
| `34_fx_currency_forecast.py` | Currency ETF (FXE) close with USD-index covariate | Yahoo Finance connector (no key needed) |
| `41_include_pending_whatif.py` | **`include_pending` what-if** — preview accepted-but-pending discovered rules before the approval gate, then activate | `data/fred_economic_data.csv` |
| `45_residual_diagnosis.py` | Diagnose a forecast miss as **drift vs correction** (`residual_diagnosis`, preview) | `data/fred_economic_data.csv` |

`26_neurosymbolic_bond_yield.py` is the headline forecasting walkthrough: it
trains a model, **discovers explainable correction rules** from its residuals
(each printed with its fire-rate and backtest delta), reads a transparent
**symbolic forecast with its WHY**, and ends with the honest **neural vs
neurosymbolic** R²/RMSE comparison — so you can see whether the symbolic layer
earns its place. Needs a user-scoped key (`at_...`): discovery is a write
operation.

### Agent Policy Gate demos

Author the rules an AI agent must obey in **plain English**; Ambertrace compiles
them to a verified policy and **proves every proposed tool-call permit/deny** —
fail-closed, with a machine-checked proof. No dataset: policies are
English-authored. The gate is a **preview** capability — these demos report
cleanly and skip when it isn't enabled on your deployment (HTTP 404).

| Script | Obligation class | What it shows |
|--------|------------------|---------------|
| `25_agent_spend_budget.py` | Cumulative exposure (Σ qty × price) | Mediated session caps total committed spend; `--band` adds the interval-band variant |
| `35_agent_rate_limit.py` | Cumulative count | Mediated session caps notifications sent per session |
| `36_agent_tool_allowlist.py` | Per-action condition | Single-action gating: tool allowlist + a safe numeric band (the simplest gate) |
| `37_agent_pii_egress_gate.py` | Per-action condition | Single-action gating: block outbound payloads containing SSN / credit-card data |
| `47_agent_position_limit.py` | Cumulative sum | Mediated session caps a running position (Σ quantity) at a lot limit |
| `48_agent_loop_gated.py` | (integration) | A real agent loop: a planner proposes actions, the gate vets each, the agent replans on a deny |
| `52_policy_gallery.py` | (discovery) | Browse the built-in `examples()` policy library and author one programmatically |

### SDK mechanics demos

Small demos of the SDK's operational surface — error handling and build
diagnostics — rather than a particular industry domain.

| Script | What it shows | Writes data? |
|--------|---------------|--------------|
| `38_error_handling.py` | `AmbertraceError` fields (status_code/code), verified 503 fail-closed, the two `wait_for_job` job types | No (read-only) |
| `39_build_diagnostics.py` | Read `generation_diagnostics` from the build job — explain whether a platform can reach an adverse decision | Yes |

### Platform governance & data-source demos

Exercise the rule-governance, domain-configuration, and connector surfaces.

| Script | What it shows | Data |
|--------|---------------|------|
| `40_rule_review_loop.py` | Human-in-the-loop rule governance: `suggest_rules` → `approve`/`reject` → `update_rule` (activate/deactivate) | `data/loan_applications.csv` |
| `42_domain_eval_and_feedback.py` | Domain eval-config (`suggest`/`set`/`get`) + `feedback_stats` | `data/vehicle_inspections.csv` |
| `43_domain_templates.py` | Reusable domain rule templates (list/create/update/delete) | `data/vehicle_inspections.csv` |
| `44_rest_connector.py` | Ingest from a generic REST/JSON endpoint (bring-your-own-auth headers) | `rest` connector |

Domain demos support `--standard` (skip verified profile) and `--tau` (confidence
threshold) flags. They create resources on your account but do not self-clean —
delete via the dashboard or API when done.

```bash
python 11_fraud_detection.py
python 12_clinical_safety.py --standard
python 18_access_governance.py
python 20_bond_yield_forecast.py
python 21_bitcoin_forecast.py -v
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
