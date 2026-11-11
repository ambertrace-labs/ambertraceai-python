# Migration notes

## 2.10.0 — the Decision Table (decision outcomes are declared, not guessed)

`2.10.0` replaces the decision-vocabulary machinery with a **Decision Table** you
declare (or confirm). The server contract is **breaking** for code that read
`decision_vocabulary` or branched on `outcome == "indeterminate"`; this SDK release is
the matching client.

**Serving: what to branch on.**

| You want to… | Branch on | Notes |
|---|---|---|
| execute vs block (permit/deny switching) | `permitted` | `True` iff the deciding row `permits` |
| run label-specific logic (route `escalate` to a human) | `decision` | always one of your table's labels, as written |
| tell "no verdict reached" apart | `status` | `decided` / `abstain` / `indeterminate` / `unavailable` |

```python
# Before
if v["outcome"] == "indeterminate":      # authorize_action / step verdicts
    supply(v["missing_inputs"])
vocab = api.platforms.status(pid)["decision_vocabulary"]   # {"verbs": [...]}

# After
if v["status"] == "indeterminate":       # outcome is now "permit" | "deny" | None
    supply(v["missing_inputs"])
table = api.platforms.status(pid)["decision_table"]        # {"mode", "rows", "provenance", "applied"}
```

* `abstain` is a `status`, never a `decision` string; `outcome` / `permitted` are
  `None` when nothing was decided (and always in `partition` mode).
* `QueryResult` now types `outcome`, `permitted` and `status` (`status` is served once the
  decision-table query path ships; `None`/absent on an older server).
* `decision_vocabulary` (on `platforms.status`, `AuthorResult`, `AgentPolicyStatus`) and
  `vocabulary_declared` (on a query result's `explanation`) are **removed**; read
  `decision_table`. A rule's `action_type` in `symbolic_trace.rules[]` is now `derive` or
  `decide`; an abstain is `status: "abstain"` with `decision: None`, never a decision
  string.

**Declaring the table (new).**

```python
api.domains.create(name=..., description=..., decision_table=TABLE)   # create + set
api.domains.set_decision_table(domain_id, TABLE)                      # confirm / edit
api.agent_policy.author(policy_text, decision_table=TABLE)            # gates: omit => {permit, deny}
```

A table is `{"mode": "ladder" | "partition", "rows": [{"label", "order", "default",
"permits", "values"}, ...]}`. Where a dataset's decision column holds cells that differ
from your labels, list them in the row's `values` (e.g. loan `approved` / `denied`,
recruitment `Hired` / `Rejected`). If you declare nothing, the platform proposes a table
from the data's label column or your description: read it, with its `provenance` and
`guessed` fields and the consistency checks, from
`datasets.quality(id)["decision_table"]` BEFORE building. A build is refused (409) when a
decision-column value maps to no row; other findings are advisory
(`platforms.status(id)["decision_table_warnings"]`). Edits take effect on the next build.

**`domains.get` / `platforms.status` / `author` / `agent_policy.status`** all echo
`decision_table`. See `examples/71_decision_table_quickstart.py`; the deciding examples
(11-15, 18, 19, 24, 25, 27, 29, 31, 36-39, 41, 68) each declare theirs.

---

# Migrating to 1.0.0

`ambertraceai` 1.0.0 is the first stable release. It lands **three breaking
default flips** together. The SDK is onboarding its first customers, so the
correct defaults are set now, while few consumers depend on the old behaviour.

Each change has an **escape hatch** that restores the pre-1.0.0 behaviour. If you
pass the escape-hatch argument everywhere, upgrading to 1.0.0 is a no-op.

---

## C1 — compact certification by default

`symbolic_forecast` now returns a **compact** certification by default.

**Before (≤ 0.18.x):** the full per-feature `certified_facts` list shipped on
every verified call (top-level `why_certification.certified_facts`, and a second
copy embedded in `prediction_record.why_certification`).

**After (1.0.0):** the top-level `why_certification` carries a
`certification_summary` (`{proof_checked, n_certified, n_rejected,
min_confidence}`) instead of the full list; the embedded
`prediction_record.why_certification` always carries the compact,
proof-carrying handle (never a second full copy). The full list is retrievable
by opting in.

```python
# Before — full certified_facts by default
resp = api.predictions.symbolic_forecast(platform_id=..., ...)
facts = resp["why_certification"]["certified_facts"]   # KeyError in 1.0.0

# After — opt back in to the full list (escape hatch)
resp = api.predictions.symbolic_forecast(
    platform_id=..., ..., compact_certification=False,
)
facts = resp["why_certification"]["certified_facts"]   # full list again
```

**Escape hatch:** `compact_certification=False`.

---

## C2 — `train()` blocks and returns the trained config by default

`platforms.train(...)` now defaults to `wait=True`.

**Before (≤ 0.18.x):** `train()` returned the raw 202 job envelope
(`{"config_id", "status": "training", "job_id", "poll"}`) immediately; you polled
the job yourself and re-fetched the config with `list_configs()`.

**After (1.0.0):** `train()` polls the training job to completion (using the same
machinery as `discover_prediction_rules` / `neurosymbolic_comparison`) and returns
the **settled trained `PredictionConfig`** dict. It blocks for the training
duration (bounded by `timeout`, default 600s) and its return type changed from a
job envelope to a config.

```python
# Before — raw job envelope, poll yourself
job = api.predictions.train(platform_id, config_id)
job_id = job["job_id"]                      # None / KeyError in 1.0.0
api.wait_for_job(job_id)
cfg = next(c for c in api.predictions.list_configs(platform_id)
           if c["id"] == config_id)

# After — settle-and-return (default)
cfg = api.predictions.train(platform_id, config_id)   # blocks, returns trained config
print(cfg["resolved_target_transform"], cfg["output_space"])

# Escape hatch — keep the historic raw-job return + poll yourself
job = api.predictions.train(platform_id, config_id, wait=False)
job_id = job["job_id"]
```

**Escape hatch:** `wait=False`.

---

## C3 — `predict().value` is the LEVEL by default

For a **differenced** target (`target_transform="difference"`), `predict()` now
returns the reconstructed **level** as the primary `value`.

**Before (≤ 0.18.x):** on the no-history / unreconstructed path `value` was the
raw month-over-month **change** (e.g. `0.055`) — silently, under an unchanged key.
(On the reconstructable path `value` was already the level, but with no
`value_change` alongside it.)

**After (1.0.0):** `value` is the reconstructed level (`baseline + change`, e.g.
`4.32`), the change is exposed alongside as **`value_change`**, and
`value_space == "level"`. For the reconstructable path
`value == baseline + value_change` holds by construction. When there is no base
history to reconstruct from, `value` stays the raw change and
`value_space == "transformed_unreconstructed"` (treat `value` as unreliable, and
read `value_change`).

```python
# After (differenced target, with history)
resp = api.predictions.predict(platform_id, prediction_config_id=cfg_id)
p = resp["prediction"]
p["value"]         # 4.32  -> the LEVEL (was the raw change 0.055 pre-1.0.0)
p["value_change"]  # 0.055 -> the month-over-month change, alongside
p["value_space"]   # "level"
p["baseline"]      # 4.265 -> the last observed level used to reconstruct
# invariant: p["value"] == p["baseline"] + p["value_change"]
```

There is **no escape-hatch argument** for C3 — this is a public-contract
semantics change. To recover the pre-1.0.0 change value, read `value_change`
(differenced targets) rather than `value`. A **non-differenced** target
(`target_transform` = `none`/level) is unchanged: `value` was and remains the
level, and `value_change` is `null`.

---

## Additive in 1.0.0 — no migration needed

These ship in 1.0.0 alongside the three flips but require **no code change**:

### Typed convenience returns (`TypedDict`)

Every convenience method now declares a `TypedDict` return type
(`query(...) -> QueryResult`, `authorize_action(...) -> AuthorizeActionResult`,
`symbolic_forecast(...) -> SymbolicForecastResult`, `platforms.get(...) ->
PlatformOut`, …) instead of a bare `dict`. **This is annotation-only.** A
`TypedDict` *is* a `dict` at runtime — the object returned is the same
`AttrDict` as before — so `result["answer"]`, `result.answer`, `result.get(...)`,
`in`, `**spread` and `json.dumps(result)` all keep working byte-for-byte. You
gain IDE autocomplete and a type-checker that catches a field typo
(`result["desicion"]` → error). Nothing to migrate.

```python
# unchanged access — still a dict
r = api.platforms.query(pid, query="…")
r["answer"]        # works
r.answer           # works
r.get("decision")  # works
# NEW: your IDE now autocompletes r["…"] and a type-checker flags r["desicion"]
```

The shapes live in `ambertraceai.responses` and are exported from the top-level
package, so you can annotate your own code (`def handle(r: QueryResult): ...`) or
ignore them entirely. Genuinely open sub-blocks (`explanation`, the raw
`prediction`, `why_certification`) are typed as an open `dict[str, Any]` (aliased
`JsonDict`).

### DX doc / example fixes (behaviour unchanged)

- `create_config` now documents `mode` (`cross_sectional` vs `timeseries`) as its
  primary switch and what it means for `feature_overrides`.
- `datasets.fetch` / `datasets.clean` now document their async
  `processing`→`ready` poll (like `fetch_multi`).
- A dangling `PlatformResource.prediction_model` docstring reference was removed.
- `wait_for_job` / `JobResource.get` now accept `int | str` job ids.
- `examples/06_predictions.py` was corrected to the real `predict(...)` /
  `train(...)` signatures; `examples/02_platform_lifecycle.py` now polls
  build-ontology by its returned `job_id` (agreeing with the README/docstring).
