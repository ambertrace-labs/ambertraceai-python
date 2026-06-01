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
