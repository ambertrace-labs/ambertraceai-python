"""48 — Gated Agent Loop (planner proposes, the Policy Gate vets, the agent REPLANS).

The headline integration: a REAL agent loop where a planner PROPOSES actions and
the verified Policy Gate VETS each one BEFORE it executes. Unlike 25/35/47 — which
step a fixed, hard-coded stream — here the agent REACTS to the gate's verdicts: a
permit executes (and joins the ledger); a deny is an observation the agent learns
from and REPLANS around (propose something smaller, retry). The control loop is
closed by the proof, not by a script.

The scenario reuses the cumulative SPEND-BUDGET policy from 25, authored in PLAIN
ENGLISH: the running sum of ``quantity x unit_price`` over the order ledger must
stay at or below BUDGET. Individually every order is fine — the control is the
CUMULATIVE total, which a per-action check cannot express. The agent BELIEVES it
has some budget and proposes ``place_order`` actions; the gate proves each one
against the accumulated executed-action ledger and permits or denies, fail-closed.
The mediation invariant holds throughout: an effect occurs IFF the gate returned a
permit with a checked proof.

What it shows:

  1. Author the cumulative spend-budget policy in ENGLISH (no dataset upload)
  2. Read back the admitted verified rule(s) + the declared input fields an action
     must supply
  3. Run a closed-loop agent: the planner PROPOSES an order, the gate VETS it, and
     the agent ADAPTS — on permit it records the spend and continues; on deny it
     REPLANS a smaller order and retries; when even the smallest order is denied it
     STOPS (budget exhausted). At the end the session trace proves executed-vs-
     proposed and the invariant that effects only follow a certified permit.

The default planner is DEPENDENCY-FREE and deterministic (reproducible). An OPTIONAL
Claude-backed planner is used only when the ``anthropic`` package is importable, an
``ANTHROPIC_API_KEY`` is set, AND ``--llm`` is passed; on any error it falls back to
the deterministic planner. ``anthropic`` is NOT a dependency of this SDK — it is an
optional runtime import.

This is a verified GATE, not a dataset-trained platform — the policy is authored
from English, so there is no domain/data upload step. The Agent Policy Gate is a
preview capability; when it is not enabled on your deployment the endpoints return
404, which this demo reports cleanly and skips.

Creates resources on your account. Run with --help for options.

    python 48_agent_loop_gated.py
    python 48_agent_loop_gated.py --rounds 8
    python 48_agent_loop_gated.py --llm        # use a Claude planner if available
"""

from __future__ import annotations

import argparse
import os

from ambertraceai import AmbertraceError

from _common import add_common_args, print_section, run_demo

# The budget. Cumulative spend = sum of (quantity x unit_price) over the ledger.
BUDGET = 100_000

# A cumulative-exposure policy, authored in plain English (identical in spirit to
# 25). The compiler admits a verified EXPOSURE obligation: the sum of quantity x
# unit_price over the order ledger must stay at or below BUDGET.
SPEND_POLICY = (
    "An autonomous procurement agent may place purchase orders. Each order is "
    "recorded as a row in a purchase_orders ledger with a quantity column and a "
    "unit_price column. The cumulative spend — the sum of quantity times "
    "unit_price across every row in the purchase_orders ledger — must stay at or "
    f"below {BUDGET}. Permit a purchase order only when the resulting cumulative "
    "spend stays within that budget."
)

# The planner's opening move: 100 units @ 400 = 40,000 of exposure per order.
START_QTY = 100
UNIT_PRICE = 400
# Below this quantity the agent considers the order too small to bother with: if
# even this is denied, the budget is exhausted and the agent stops.
MIN_QTY = 12


def _print_admitted(result: dict) -> None:
    admitted = result.get("admitted") or []
    rejected = result.get("rejected") or []
    print(f"  Admitted {len(admitted)} verified rule(s):")
    for rule in admitted:
        desc = (rule.get("description") or rule.get("name") or "").strip()
        print(f"    - {rule.get('name')}: {desc}")
    if rejected:
        print(f"  Rejected {len(rejected)} proposal(s) (outside the verified fragment):")
        for r in rejected:
            print(f"    ! {r.get('name')}: {r.get('reason')}")


def _print_inputs(status: dict) -> None:
    inputs = status.get("input_fields") or []
    if not inputs:
        # No declared inputs at all (e.g. a policy with no per-action operands).
        print("  No declared input fields: the gate still constrains whatever the "
              "action proposes.")
        return
    # A cumulative-exposure policy reads its operands (quantity / unit_price) from
    # the LEDGER ROW each action contributes; those operand columns are surfaced as
    # input_fields, so an action supplies them as args and the gate proves the
    # obligation over the resulting ledger.
    print(f"  Declared input fields an action must supply ({len(inputs)}):")
    for spec in inputs:
        rng = ""
        if spec.get("min_value") is not None or spec.get("max_value") is not None:
            rng = f" [{spec.get('min_value')}..{spec.get('max_value')}]"
        print(f"    - {spec.get('name')} ({spec.get('type')}){rng}")


# ---------------------------------------------------------------------------
# The planner: PROPOSES the next action from the agent's own (believed) state.
# ---------------------------------------------------------------------------

class DeterministicPlanner:
    """A dependency-free, reproducible planner.

    State the planner tracks: ``proposed_qty`` (the size of the next order it wants
    to place). It opens with a large order and, each time the gate DENIES, halves
    the quantity it proposes (an integer floor) — the agent's reaction to a refusal
    is to scale back, not to keep banging on the same denied action. A permit does
    not change the proposed size: the agent keeps trying the same order until the
    gate stops it, which is exactly how the cumulative ceiling is discovered.
    """

    name = "deterministic"

    def __init__(self) -> None:
        self.proposed_qty = START_QTY

    def propose(self, state: dict) -> dict:
        """Return the next proposed action {tool, quantity, unit_price}."""
        return {
            "tool": "place_order",
            "quantity": int(self.proposed_qty),
            "unit_price": UNIT_PRICE,
        }

    def on_deny(self, state: dict) -> None:
        """React to a refusal: propose a SMALLER order next time."""
        self.proposed_qty = self.proposed_qty // 2


class ClaudePlanner:
    """OPTIONAL planner backed by the Anthropic Messages API.

    Used only when ``anthropic`` is importable, ``ANTHROPIC_API_KEY`` is set, and
    ``--llm`` is passed. It asks Claude for the next {quantity, unit_price} given the
    refusal history; it is small and DEFENSIVE — any error (import, network, parse,
    bad shape) raises and the caller falls back to the deterministic planner.

    ``anthropic`` is NOT a dependency of this SDK; it is imported lazily here.
    """

    name = "claude"

    def __init__(self) -> None:
        import anthropic  # optional runtime import — lazy on purpose

        self._client = anthropic.Anthropic()
        self._fallback = DeterministicPlanner()
        self._history: list[str] = []

    def propose(self, state: dict) -> dict:
        try:
            return self._ask_claude(state)
        except Exception as exc:  # defensive: any failure -> deterministic
            print(f"    (Claude planner error: {exc} — falling back to deterministic)")
            return self._fallback.propose(state)

    def on_deny(self, state: dict) -> None:
        self._fallback.on_deny(state)
        self._history.append(
            f"DENIED a {state.get('last_qty')}-unit order at unit_price "
            f"{UNIT_PRICE}; believed remaining budget {state.get('believed_remaining')}."
        )

    def _ask_claude(self, state: dict) -> dict:
        import json

        history = "\n".join(self._history) or "(no refusals yet)"
        prompt = (
            "You are a procurement agent placing purchase orders against a "
            f"cumulative spend budget of {BUDGET}. Each order costs "
            "quantity*unit_price. You believe you have "
            f"{state.get('believed_remaining')} of budget remaining. Refusal "
            f"history so far:\n{history}\n\n"
            "Propose the SINGLE next order as strict JSON with integer fields "
            '"quantity" and "unit_price" and nothing else. Keep unit_price at '
            f"{UNIT_PRICE}. After a refusal, propose a SMALLER quantity."
        )
        msg = self._client.messages.create(
            model="claude-opus-4-8",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )
        text = next((b.text for b in msg.content if b.type == "text"), "").strip()
        # Be defensive about fences / surrounding prose: extract the JSON object.
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"no JSON object in model reply: {text!r}")
        data = json.loads(text[start:end + 1])
        qty = int(data["quantity"])
        price = int(data.get("unit_price", UNIT_PRICE))
        if qty <= 0 or price <= 0:
            raise ValueError(f"non-positive order: {data!r}")
        return {"tool": "place_order", "quantity": qty, "unit_price": price}


def _make_planner(args: argparse.Namespace):
    """Pick the Claude planner when requested AND available; else deterministic."""
    if not args.llm:
        return DeterministicPlanner()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("  --llm requested but ANTHROPIC_API_KEY is not set — using the "
              "deterministic planner.")
        return DeterministicPlanner()
    try:
        import anthropic  # noqa: F401  (probe availability)
    except ImportError:
        print("  --llm requested but the 'anthropic' package is not installed — "
              "using the deterministic planner.")
        return DeterministicPlanner()
    try:
        return ClaudePlanner()
    except Exception as exc:  # construction failure -> deterministic
        print(f"  Claude planner unavailable ({exc}) — using the deterministic "
              "planner.")
        return DeterministicPlanner()


# ---------------------------------------------------------------------------
# The closed loop: propose -> gate -> react.
# ---------------------------------------------------------------------------

def _run_agent_loop(api, platform_id: int, planner, rounds: int) -> None:
    session = api.agent_policy.create_session(
        platform_id=platform_id, goal="place purchase orders within budget")
    sid = session["id"]
    print(f"  Mediated session {sid} opened (the gate is the sole executor).")
    print(f"  Planner: {planner.name}.  Believed budget to start: {BUDGET}.\n")

    believed_spent = 0          # what the agent THINKS it has committed
    proposed_count = 0
    executed_count = 0

    for round_no in range(1, rounds + 1):
        state = {
            "round": round_no,
            "believed_remaining": BUDGET - believed_spent,
            "last_qty": None,
        }
        action = planner.propose(state)
        qty, price = action["quantity"], action["unit_price"]
        state["last_qty"] = qty
        exposure = qty * price
        proposed_count += 1

        print(f"  {'-' * 66}")
        print(f"  Round {round_no}: PROPOSE place_order qty={qty} @ {price} "
              f"(exposure {exposure:,}; believed remaining {BUDGET - believed_spent:,})")

        step = api.agent_policy.step(
            sid, tool="place_order", args={"quantity": qty, "unit_price": price})
        verdict = (step.get("step") or {}).get("verdict") or {}
        executed = (step.get("step") or {}).get("executed")
        decision = verdict.get("decision")

        print(f"    Decision:      {str(decision).upper()}")
        print(f"    proof_checked: {verdict.get('proof_checked')}")
        print(f"    executed:      {executed}")

        if decision == "permit":
            # The order joined the ledger — the agent updates its belief and
            # keeps going with the same plan.
            if executed:
                executed_count += 1
                believed_spent += exposure
            print(f"    REACTION:      recorded — believed spent now "
                  f"{believed_spent:,}; continuing.")
            continue

        # Deny: the agent OBSERVES the refusal and REPLANS smaller.
        if verdict.get("denied_reason"):
            print(f"    denied_reason: {verdict.get('denied_reason')}")
        planner.on_deny(state)
        next_action = planner.propose(state)
        next_qty = next_action["quantity"]
        if next_qty < MIN_QTY:
            print(f"    REACTION:      stopping — budget exhausted (smallest viable "
                  f"order {next_qty} < {MIN_QTY}).")
            break
        print(f"    REACTION:      replanning smaller — will propose qty={next_qty} "
              "next round.")

    # The session trace proves the mediation invariant: only permitted orders ran.
    trace = api.agent_policy.get_session(sid).get("trace") or []
    executed_in_trace = [t for t in trace if t.get("executed")]
    print(f"\n  {'=' * 66}")
    print(f"  Loop complete. Proposed {proposed_count} order(s) across the agent's "
          f"reactions;")
    print(f"  executed {len(executed_in_trace)} of {len(trace)} step(s) in the "
          "session trace.")
    print(f"  Believed committed spend: {believed_spent:,} (budget {BUDGET:,}).")
    print("\n  PROVEN INVARIANT: every executed order is preceded by a certified "
          "permit — an")
    print("  effect occurs only after the kernel proved the cumulative spend stays "
          "within budget.")


def _author(api, policy_text: str):
    """Author the policy; return the result dict, or None on a 404 preview-skip."""
    try:
        return api.agent_policy.author(policy_text)
    except AmbertraceError as exc:
        if getattr(exc, "status_code", None) == 404:
            print("\n  The Agent Policy Gate is not enabled on this deployment "
                  "(preview capability) — skipping.")
            return None
        raise


def run_agent_loop_demo(api, args: argparse.Namespace) -> None:
    print_section(1, 3, "Authoring the spend-budget policy (English in)")
    print(f"  POLICY:\n    {SPEND_POLICY}\n")

    print_section(2, 3, "Reviewing the admitted verified rules + declared inputs")
    result = _author(api, SPEND_POLICY)
    if result is None:
        return
    platform = result.get("platform") or {}
    print(f"  Authored verified policy -> platform {platform.get('id')} "
          f"({platform.get('status')}, verified={platform.get('verified_profile')})")
    _print_admitted(result)
    _print_inputs(api.agent_policy.status())

    print_section(3, 3, "Running the gated agent loop (propose -> vet -> replan)")
    planner = _make_planner(args)
    _run_agent_loop(api, platform["id"], planner, args.rounds)

    print("\nDone. The planner reacted to the gate's verdicts in a closed loop: "
          "permits executed and joined the ledger, denials drove the agent to "
          "replan smaller, and the budget was discovered through proof — never "
          "default-allowed.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Gated Agent Loop — AmberTrace AI verified cumulative-exposure "
                    "governance in a closed propose/vet/replan loop (English-authored)",
    )
    add_common_args(parser)
    parser.add_argument(
        "--rounds", type=int, default=6,
        help="Maximum number of propose/vet rounds the agent runs (default: 6).",
    )
    parser.add_argument(
        "--llm", action="store_true",
        help="Use a Claude planner if available (requires the optional 'anthropic' "
             "package + ANTHROPIC_API_KEY); otherwise the deterministic planner runs.",
    )
    args = parser.parse_args()
    run_demo(run_agent_loop_demo, args)


if __name__ == "__main__":
    main()
