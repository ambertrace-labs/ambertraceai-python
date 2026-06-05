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

### Forecasting demos

Time-series and scenario forecasting via the prediction API. Create a domain,
ingest data (from CSV or a built-in connector), train a model, and run
what-if scenarios.

| Script | Domain | Data source |
|--------|--------|-------------|
| `20_bond_yield_forecast.py` | US 10y Treasury yield (macro) | `data/fred_economic_data.csv` or FRED connector (`FRED_API_KEY`) |
| `21_bitcoin_forecast.py` | BTC-USD daily price | Coinbase connector (no key needed) |
| `22_equity_forecast.py` | SPY daily price | Yahoo Finance connector (no key needed) |

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
