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
| `25_cross_domain_cueing.py` | Cross-domain cueing — unified air+maritime `fused_track` triage with a top-precedence cross-cue rule, a separate human-review obligation, and a derived position-trust flag (Tier 0). The two cross-domain cue booleans are **pre-joined by the fusion layer outside the proof** — the certified claim is conditional on them (Tier 1 brings the join inside) | `data/fused_tracks.csv` (regenerate via `python gen_fused_tracks.py`) |
| `38_symmetric_multiclass_classifier.py` | **Symmetric N-class / multiclass classification** — classify an observation into ONE of N mutually-exclusive labels (the 2×2 macro-regime grid: reflation / goldilocks / stagflation / deflation), each answer proof-carrying. The class labels ARE the platform's decision verbs — a verified DOMAIN platform, NOT the `author()` permit/deny gate | `data/macro_regime_panel.csv` (seeded features-only on first run) |
| `39_federal_ethics_gift_gate.py` | **Federal gift-acceptance ethics gate (5 CFR 2635 Subpart B)** — encodes the executive-branch Gifts From Outside Sources rules as a **classify-then-conclude** permit/decline/**escalate** domain: the codifiable core (bribery + cash-equivalent overrides, the $20-per-source-per-occasion and $50-annual thresholds, excluded items) is proved; the open-textured reasonable-person appearance test is **not forced into logic** — it *escalates* to a human. First-matching-rule precedence (bribe-decline beats the $20 exception; escalate beats permit), `decline` as the fail-closed default. 14/14 CFR worked examples decide as the regulation requires, each proof-carrying. Illustrative encoding — not legal advice, not affiliated with any agency | `data/gift_acceptance_cases.csv` |

### Multi-class (N-class) classification

Need to classify into one of **N labels** rather than permit/deny? That is a
verified **domain platform** whose decision verbs *are* the class labels — you
author it through the ordinary `domains` → `build_ontology` → `platforms` surface.
There is **no `multiclass` model_type and no new SDK method**, and it does **not**
use the `author()` permit/deny gate (that gate's only outcomes are
permit/deny/indeterminate/unavailable — a different shape entirely).

See **`38_symmetric_multiclass_classifier.py`** for the copy-me template and the
English-phrasing recipe that makes every class resolve:

1. Define each **axis** with an explicit threshold **and** an `otherwise` clause
   ("growth is firm when real GDP growth is at least 2.0 percent, otherwise soft").
2. Define each **label** as a **conjunction of axis states** ("reflation is firm
   growth with elevated inflation") — one label per cell of the grid.
3. State completeness: "Every observation must be classified into exactly one
   regime." — a total, mutually-exclusive partition, not overlapping flags.

Query it with `platforms.query(...)` and read `report["decision"]` (the winning
label) plus `report["proof_checked"]`. It scales to flat N≈6–8 labels and small
`k`-axis grids — author grids **compositionally** (`k` axis-classifiers plus one
label-per-cell layer), not by enumerating `mᵏ` cells.

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
| `28_agent_policy_gate_cicd.py` | CI/CD deploy gate — a software-supply-chain policy (enum allowlist + boolean preconditions + canary-rollout cap + **separation of duties: approver ≠ author**, a cross-field inequality); gates a compliant deploy (permit) and several single-fact-flipped cases including the SoD violation (deny). This one stays PER-ACTION and expresses change-window / review-before-merge as caller-supplied booleans; for a NATIVE happens-before obligation proved from the ordered ledger, see `40_agent_policy_gate_temporal.py` |
| `30_investment_decision_gate.py` | Investment decision-process gate — proves an AI execution agent followed a fiduciary decision process before any trade stands. **Tier-partitioned conditional permits** (`trade_tier` standard/material as the mutually-exclusive partition) + cross-field suitability comparison + concentration caps + restricted-list block + **separation of duties on material trades: approver ≠ recommender**. Synthetic/illustrative CFA Code & Standards encoding — not investment advice, not affiliated with CFA Institute |
| `25_agent_spend_budget.py` | Cumulative spend budget — mediate a session so the obligation is proven over the accumulated ledger (with a `--band` interval variant) |
| `40_agent_policy_gate_temporal.py` | **Temporal precedence (review-before-deploy)** — a NATIVE happens-before obligation authored in English (`precededBy`): a deploy permits only when an approval for the SAME service preceded it in the session's ORDERED ledger. Mediates sessions to show the order-sensitivity payoff (approve-then-deploy permits; deploy-then-approve and un-preceded deploy both deny) — the thing a caller-supplied boolean cannot do |

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
| `32_inflation_macro_forecast.py` | US CPI inflation (INFL_YOY) — system picks the macro drivers | `data/inflation_macro_panel.csv` (bundled, FRED public domain) |
| `33_credit_spread_macro_forecast.py` | US investment-grade credit spread (IG_SPREAD) — system picks the drivers | `data/credit_macro_panel.csv` (bundled, FRED public domain) |
| `34_real_gdp_growth_macro_forecast.py` | US real GDP growth (REAL_GDP_GROWTH) — system picks the drivers | `data/gdp_macro_panel.csv` (bundled, FRED public domain) |
| `35_geopolitical_risk_macro_forecast.py` | Geopolitical risk (GPR, Caldara-Iacoviello index) — system picks the drivers; an honest read on how little macro explains an EXOGENOUS target | `data/geopol_macro_panel.csv` (bundled; GPR index public — cite matteoiacoviello.com on reuse; macro panel FRED public domain) |

These are **classical / symbolic** forecasters — a gradient-boosted model over a broad
macro panel plus an induced set of readable WHEN→THEN driver rules and a persistence
baseline. The value is the *explained fit and the readable drivers*, not a market-beating
signal (on infrequent, freely-available macro series nobody beats a last-value baseline —
`skill_vs_persistence` is honest context, never a pass/fail gate).

### Predictions → Decision bridge

Feed a verified **forecast** into a verified **decision** so the whole chain — *data →
forecast → decision* — is one auditable artifact. Forecasting and decisioning are separate,
independently-governed platforms. There are **two** ways to bridge them; **prefer the native
by-reference path.**

| Script | What it shows |
|--------|---------------|
| `36_credit_forecast_to_loan_decision.py` | **Single** forecast → decision. One credit-spread forecast feeds one verified lending decision; the same marginal borrower APPROVES when the forecast is benign and is REFERRED when it signals tightening credit — a counterfactual proving the forecast is *material* |
| `37_multi_forecast_policy_decision.py` | **Multiple** forecasts → one decision. Three independent forecasters (inflation, GDP growth, credit spread) fan into ONE verified "monetary policy stance" decision (hike / cut / hold) |

**NATIVE path (recommended) — `query(predictions=…)`, fail-closed by reference.** Every
`symbolic_forecast(verified=True, …)` call PERSISTS its `prediction_record` server-side
(org+owner-scoped), addressable by `model_id` + `as_of`. The decision references it by handle
and the platform fetches the TRUSTED record and folds its certified `<role>.value` into the
proof — **the caller never re-supplies the forecast value** (the safety property: the
forecast's certificate certifies its input row, not that a caller-typed number followed):

```python
# Stage A — produce + persist a verified, ADDRESSABLE forecast.
api.predictions.symbolic_forecast(fc_pid, prediction_config_id=cfg_id, verified=True,
                                  prediction_name="ig_spread", as_of="2026-06-30")

# Stage B — reference it. A decision rule reads `ig_spread.value` (declared in the
# decision domain). Missing / uncertified / mis-aligned → the fact is absent → the
# decision ABSTAINS (fail-closed), it does not approve on an unproven number.
report = api.platforms.query(
    decision_pid, query="What is the lending decision?",
    facts={"credit_score": 700, "debt_to_income_ratio": 0.30},
    predictions={"ig_spread": {"model_id": "ig_spread", "as_of": "2026-06-30"}})
report["decision"]        # 'approve' | 'refer' | 'deny', with report["proof_checked"] == True
```

For **N** forecasts, reference N roles in the SAME `predictions=` map (fail-closed over a
partial fan-in). The same map is accepted by `agent_policy.authorize_action(predictions=…)`
to fan a certified forecast into the Agent Policy Gate.

**MANUAL path (what demos 36/37 currently RUN, for illustration) — `facts=` value-passing.**
Read `prediction_record["value"]` yourself and pass it as a plain `facts` scalar. It is
certified through the fact gate like any ground fact, but the CALLER supplies the number, so
you own the trust that it came from the certified forecast. Use it for counterfactuals (the
`--*-value` flags) or when the native path does not fit:

```python
sf = api.predictions.symbolic_forecast(fc_pid, prediction_config_id=cfg_id, verified=True,
                                       prediction_name="ig_spread", as_of="2026-06-30")
spread = sf["prediction_record"]["value"]        # the reconstructed LEVEL (e.g. 0.58)
report = api.platforms.query(
    decision_pid, query="What is the lending decision?",
    facts={"credit_score": 700, "forecast_credit_spread": spread})   # caller-supplied
```

**Four gotchas each demo preserves** (each was hit and fixed while building — keep them or the
examples break):

1. **Declared + in-domain certifying fact.** The forecast field must be a DECLARED schema
   column in the decision domain's dataset, and the queried value must be IN-DOMAIN (within
   the column's observed range) — otherwise the verified fact gate rejects it. The demos ship
   a small seeded synthetic dataset that *declares* the forecast field(s) spanning a realistic
   range, and clamp live forecasts into that range defensively.
2. **Build-time stratification — never "otherwise approve/hold".** Phrasing the default
   outcome as "otherwise approve" gets induced as "approve if NOT (deny OR refer)", making the
   outcome depend on the negation of *itself* → the verified build is rejected as
   **non-stratifiable**. Fix: route the decision through intermediate *classification* atoms
   (`blocked`, `needs manual review`, `rate hike is warranted`, …) and define each outcome over
   those, so negation is only ever over a lower-stratum atom, never the outcome.
3. **Query-time reachability — intermediate atoms must use POSITIVE conditions** (distinct from
   #2). An intermediate atom defined with *internal* negation (e.g. "tightening is warranted
   when inflation is hot and growth is **not** weak") builds fine but the verified engine
   **abstains at query time** — *"a declared restrictive outcome has no reachable certifying
   path"* — because the negated intermediate never derives. Fix: define intermediate warrant
   atoms with only positive classifications ("… and growth **is strong**"), and keep negation
   solely at the FINAL outcome layer ("cut when a cut is warranted and a hike is **not**
   warranted"). Final-layer negation over already-derived intermediate atoms is fine; it is
   negation *inside* an intermediate atom that breaks reachability.
4. **Read the LEVEL, not the transform.** Read `symbolic_forecast(...)["prediction_record"]
   ["value"]` — the canonical Stage-A output, always LEVEL space and always present. A raw
   `predict(...)["prediction"]["value"]` is LEVEL by default in 1.0.0 but can be a raw change on
   the no-history path (`value_space == "transformed_unreconstructed"`); prefer the record.

**This is the ship-now, manual-scalar-fact pattern.** The decision certifies against the
forecast's *value*; the forecast's own certificate (`why_certification` / `proof_ref`, both on
the `prediction_record`) is available but not yet re-checked at the seam. A first-class,
proof-carrying `PredictionRecord` handoff — where a decision fans in named prediction records
by role and chains each one's proof multi-parent, fail-closed — is a roadmap item; when it
lands, these same two demos become the before/after that shows why it matters.

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
