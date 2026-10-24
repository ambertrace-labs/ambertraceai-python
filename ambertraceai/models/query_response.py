from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_response_decision_table_type_0 import QueryResponseDecisionTableType0
    from ..models.query_response_explanation_type_0 import QueryResponseExplanationType0


T = TypeVar("T", bound="QueryResponse")


@_attrs_define
class QueryResponse:
    """
    Attributes:
        answer (str):
        platform_id (int):
        query (str):
        decision (None | str | Unset): The deciding row's LABEL from the platform's Decision Table (``decision_table``),
            exactly as the customer declared it (e.g. ``approve``, ``deny``, ``escalate``) -- always a declared row label,
            never an internal word. ``null`` when ``status`` is ``abstain`` (no decision could be certified) or the platform
            has no decision layer. A query that fires no verdict is ``abstain`` (fail-closed) unless the platform was built
            with ``decision_posture='default_allow'``. Branch on ``permitted`` for execute-or-block and on ``decision`` for
            label-specific logic. ``explanation.decision.decision`` carries the same label.
        decision_table (None | QueryResponseDecisionTableType0 | Unset): The Decision Table the platform was built with
            {mode, rows: [{id, label, order, default, permits, values}], provenance, applied}. ``null`` when none is
            declared.
        explanation (None | QueryResponseExplanationType0 | Unset): Full explainability trace (present only when
            ``explain=True``). A DOCUMENTED, VERSIONED contract for dense-reward / audit consumers. Pinned keys:
            * ``schema_version`` (int) — the trace schema version; pin/validate against it (currently 1). Bumped on any
            breaking shape change.
            * ``symbolic_trace`` — ``{description, rules_evaluated, rules_fired, rules: [...]}``. Each ``rules[]`` item:
            ``rule_id`` (int|null), ``rule_name`` (str, stable identifier), ``rule_type`` (str, e.g.
            ``derive``/``constraint``), ``action_type`` (``derive`` | ``decide`` | the annotation word, str|null), ``fired``
            (bool — on a VERIFIED platform this reflects the KERNEL-CERTIFIED firing set, reconciled against
            ``proof.firings``, not the engine self-report), ``required`` (bool — True for a hard obligation: a ``require``
            leaf or a decision whose row does not permit; False for a supporting/informational rule), ``explanation`` (str).
            BOTH fired and unfired rules are listed (the 'which fired vs. which existed' dense-reward signal).
            * ``certified_facts`` — list of accepted-fact records ``{field, value, confidence, schema_ok, witness_invalid,
            reasons, source, certificate}`` (verified platforms).
            * ``certified_fact_summary`` — ``{accepted, emitted, rejected, witness_invalid}`` counts (verified platforms).
            * ``rejected_facts`` — list of ``{field, value?, reasons: [...]}`` for facts rejected at the certified-fact
            gate.
            * ``confidence`` — ``{overall, neural_confidence, symbolic_confidence, neural_weight, symbolic_weight,
            symbolic_normaliser}`` (fused confidence + methodology).
            * ``proof`` — the machine-checked derivation ``{inputs, derived: [{field, value, by, stratum}], firings: [{rule,
            action, stratum}], facts}`` (verified platforms).
            * ``decision`` — the certified verdict ``{decision, deciding_rules: [{rule, reason}]}`` (decision platforms).
            ``rules[].required`` and the verified ``fired`` reconciliation are purely additive — they change no decision. On
            any internal error the rules are left exactly as produced (fail-closed).
        outcome (None | str | Unset): ``permit`` when the deciding row ``permits``, else ``deny``. ``null`` when
            ``status`` is ``abstain``, when the Decision Table is a ``partition`` (cells carry no permittedness), or when
            the platform has no decision layer. Mirrors ``outcome`` on ``authorize-action``.
        permitted (bool | None | Unset): ``outcome == "permit"``: ``True`` when the deciding row ``permits`` (the action
            is within policy), ``False`` when it does not or when ``status`` is ``abstain`` (fail-closed). ``null`` for a
            ``partition`` table and for platforms with no decision layer. Mirrors ``permitted`` on ``authorize-action``.
        proof_checked (bool | None | Unset): Verified profile only. ``True`` when the decision was independently re-
            derived and verified (the active rule set satisfies the platform's invariant manifest and the proof certificate
            is valid). ``null`` for non-verified platforms (no proof is generated). A verified query that cannot be
            certified returns HTTP 503 rather than ``proof_checked: false``.
        proof_summary (None | str | Unset): Human-readable summary of the machine-checked certificate (rules fired,
            facts derived, input facts). ``null`` for non-verified platforms. The full derivation proof and any
            ``rejected_facts`` are in ``explanation.proof`` / ``explanation.rejected_facts``.
        status (None | str | Unset): ``decided`` -- a Decision Table row decided (``decision`` is its label);
            ``abstain`` -- no decision could be certified (an equal-precedence conflict, a partition with zero or several
            cells firing, or an incomplete restrictive layer), ``decision`` is ``null``, ``permitted`` is ``false``.
            ``null`` for platforms with no decision layer. A request whose inputs the policy needs but were not supplied
            (``indeterminate``) or an unavailable engine (``unavailable``) fails closed with HTTP 503, never a decision.
    """

    answer: str
    platform_id: int
    query: str
    decision: None | str | Unset = UNSET
    decision_table: None | QueryResponseDecisionTableType0 | Unset = UNSET
    explanation: None | QueryResponseExplanationType0 | Unset = UNSET
    outcome: None | str | Unset = UNSET
    permitted: bool | None | Unset = UNSET
    proof_checked: bool | None | Unset = UNSET
    proof_summary: None | str | Unset = UNSET
    status: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_response_decision_table_type_0 import QueryResponseDecisionTableType0
        from ..models.query_response_explanation_type_0 import QueryResponseExplanationType0

        answer = self.answer

        platform_id = self.platform_id

        query = self.query

        decision: None | str | Unset
        if isinstance(self.decision, Unset):
            decision = UNSET
        else:
            decision = self.decision

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, QueryResponseDecisionTableType0):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        explanation: dict[str, Any] | None | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        elif isinstance(self.explanation, QueryResponseExplanationType0):
            explanation = self.explanation.to_dict()
        else:
            explanation = self.explanation

        outcome: None | str | Unset
        if isinstance(self.outcome, Unset):
            outcome = UNSET
        else:
            outcome = self.outcome

        permitted: bool | None | Unset
        if isinstance(self.permitted, Unset):
            permitted = UNSET
        else:
            permitted = self.permitted

        proof_checked: bool | None | Unset
        if isinstance(self.proof_checked, Unset):
            proof_checked = UNSET
        else:
            proof_checked = self.proof_checked

        proof_summary: None | str | Unset
        if isinstance(self.proof_summary, Unset):
            proof_summary = UNSET
        else:
            proof_summary = self.proof_summary

        status: None | str | Unset
        if isinstance(self.status, Unset):
            status = UNSET
        else:
            status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "answer": answer,
                "platform_id": platform_id,
                "query": query,
            }
        )
        if decision is not UNSET:
            field_dict["decision"] = decision
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if outcome is not UNSET:
            field_dict["outcome"] = outcome
        if permitted is not UNSET:
            field_dict["permitted"] = permitted
        if proof_checked is not UNSET:
            field_dict["proof_checked"] = proof_checked
        if proof_summary is not UNSET:
            field_dict["proof_summary"] = proof_summary
        if status is not UNSET:
            field_dict["status"] = status

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_response_decision_table_type_0 import QueryResponseDecisionTableType0
        from ..models.query_response_explanation_type_0 import QueryResponseExplanationType0

        d = dict(src_dict)
        answer = d.pop("answer")

        platform_id = d.pop("platform_id")

        query = d.pop("query")

        def _parse_decision(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decision = _parse_decision(d.pop("decision", UNSET))

        def _parse_decision_table(data: object) -> None | QueryResponseDecisionTableType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_table_type_0 = QueryResponseDecisionTableType0.from_dict(data)

                return decision_table_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QueryResponseDecisionTableType0 | Unset, data)

        decision_table = _parse_decision_table(d.pop("decision_table", UNSET))

        def _parse_explanation(data: object) -> None | QueryResponseExplanationType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                explanation_type_0 = QueryResponseExplanationType0.from_dict(data)

                return explanation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QueryResponseExplanationType0 | Unset, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        def _parse_outcome(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        outcome = _parse_outcome(d.pop("outcome", UNSET))

        def _parse_permitted(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        permitted = _parse_permitted(d.pop("permitted", UNSET))

        def _parse_proof_checked(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        proof_checked = _parse_proof_checked(d.pop("proof_checked", UNSET))

        def _parse_proof_summary(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        proof_summary = _parse_proof_summary(d.pop("proof_summary", UNSET))

        def _parse_status(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        status = _parse_status(d.pop("status", UNSET))

        query_response = cls(
            answer=answer,
            platform_id=platform_id,
            query=query,
            decision=decision,
            decision_table=decision_table,
            explanation=explanation,
            outcome=outcome,
            permitted=permitted,
            proof_checked=proof_checked,
            proof_summary=proof_summary,
            status=status,
        )

        query_response.additional_properties = d
        return query_response

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
