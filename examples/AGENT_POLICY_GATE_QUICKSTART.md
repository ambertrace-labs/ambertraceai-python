# Agent Policy Gate — Quickstart

Proof-carrying governance for an AI agent's actions, authored in **plain English**.
You write the rules an agent must obey; Ambertrace compiles them to a *verified*
policy and proves every proposed tool-call permit/deny against it — **fail-closed**,
with a machine-checked proof. The LLM only *proposes*; the kernel *proves*.

Everything below is under `api.agent_policy.*`. For full runnable demos see
[`27_agent_policy_gate.py`](27_agent_policy_gate.py) (single-action) and
[`25_agent_spend_budget.py`](25_agent_spend_budget.py) (cumulative session).

> **APG is *not* a dataset-trained platform.** There is no domain/data upload and no
> `decision_column` — you author *English*, not a CSV. (If you came from the domain
> ontology flow, that supervised/unsupervised distinction does not apply here.)

---

## 0. Connect

```python
from ambertraceai import AmbertraceAPI, AmbertraceError

api = AmbertraceAPI.from_env()   # reads AMBERTRACE_API_KEY (+ optional AMBERTRACE_BASE_URL)
```

**Authority matters.** The org has exactly **one** agent-policy gate. The *first*
`author()` call creates it and makes the calling user its owner. Once a gate exists,
only its **owner** or an **org-admin** may replace it. Authoring as anyone else
returns `AmbertraceError` **404** — deliberately a 404, not a 403, so the gate's
existence is not revealed to an unauthorised caller.

A 404 from `author()` therefore means **either** (a) the APG feature is not enabled on
that deployment, **or** (b) a gate already exists and your credentials lack write
authority over it. Use the gate owner's key or an org-admin key to replace it.

---

## 1. Author the policy — English in

```python
result = api.agent_policy.author(
    "The agent may place orders against an open_positions ledger with a quantity "
    "column and a price column. The cumulative exposure — the sum of quantity × "
    "price across every row — must stay at or below 100000. Permit an order only "
    "when that cumulative exposure stays within the limit."
)
platform_id = result["platform"]["id"]
```

**Always read back what was admitted — nothing is silently dropped:**

```python
for r in result["admitted"]:   # the rules admitted, each described in plain English
    print("✓", r["description"])
for r in result["rejected"]:   # anything OUTSIDE the verified fragment, WITH a reason
    print("✗", r["name"], "—", r["reason"])
```

A requirement you expected but don't see in `admitted` will appear in `rejected` with
*why* it fell outside the verified fragment. An empty/vacuous policy fails closed (422)
and leaves any existing gate unchanged.

### What you can express (the supported obligation classes)

| Class | English example |
|------|-----------------|
| **Per-action condition** | "Only allow actions of type triage, schedule, or refer." / "Require mfa_passed for privileged requests." |
| **Cumulative count / sum** | "No more than 3 actions of this kind." / "Total quantity summed across all rows must stay at or below 1000." |
| **Cumulative exposure** (`Σ qty×price ≤ limit`) | "The sum of quantity × price across every row must stay at or below 100000." |
| **Interval / band binding** | "For an order whose fill price is unknown but guaranteed between 100 and 500, exposure must stay ≤ 100000 for *every* price in that range." |

Anything outside these classes is rejected-and-surfaced, never approximated.

---

## 2. Read the input contract

```python
status = api.agent_policy.status()
for f in status["input_fields"]:    # [{name, type, enum_values?, min_value?, max_value?}]
    print(f["name"], f["type"])
```

`input_fields` is the contract for step 3 — **supply a value for every declared field**
or the gate returns a rejected/missing-fact (it never default-permits an unknown).

---

## 3a. Gate a single action — permit/deny WITH PROOF

```python
verdict = api.agent_policy.authorize_action(
    platform_id, tool="place_order", args={"qty": 100, "price": 400})

verdict["decision"]       # "permit" | "deny" | a custom verb the policy declares
verdict["proof_checked"]  # True — the verified engine certified the firing set
verdict["denied_reason"]  # on a deny, the specific requirement that failed
```

`args` are the action's intrinsic fields; pass ambient facts the policy reasons over
as `context=` (args wins on a key collision). Fail-closed: a missing/rejected fact, a
proof-check failure, or an unavailable engine yields **no permit** — never default-allow.

---

## 3b. Cumulative control? Use a session, not `authorize_action`

`authorize_action` gates against an **empty** history, so a running total (count / sum /
exposure / band) needs the accumulated ledger. Open a session — the harness is the **sole
executor** and accumulates the executed-action ledger, so the obligation is proven over
the *resulting* history:

```python
sess = api.agent_policy.create_session(platform_id=platform_id, goal="fill the book")
sid = sess["id"]

for order in proposed_orders:
    step = api.agent_policy.step(sid, tool="place_order", args=order)
    if step["decision"] != "permit":
        print("blocked at the cap:", step["denied_reason"])
        break   # the gate refused to execute it — the ledger is unchanged
```

> Using `authorize_action` for a cumulative cap silently gates against an empty ledger
> and will mislead. Per-action checks → `authorize_action`; running totals → session+`step`.

---

## The four things to get right

1. **Key/authority** — `author()` needs the gate owner's key *or* an org-admin key.
   A 404 means "not enabled" *or* "no write authority" — not "feature missing."
2. **Always test the policy** — run a within-limit action (expect permit) **and** a
   breaching one (expect deny) before relying on it. The intent safeguard is
   review + test, not a fixed vocabulary.
3. **Honour `input_fields`** — supply every declared fact; a missing fact fails closed.
4. **One-shot vs cumulative** — per-action → `authorize_action`; running total →
   `create_session` + `step`.

---

## The proof certificate is an output, not the kernel

`authorize_action` / `step` return a proof *certificate*: `decision`, `proof_checked`,
`deciding_rule`, `certified_facts`, `rejected_facts`, `denied_reason`. It demonstrates the
**result** (which facts were certified, which rule decided, that the firing set was
machine-checked). It does **not** ship or reveal the kernel / Lean formalisation that
produces it — you read the certificate; the engine stays internal.
