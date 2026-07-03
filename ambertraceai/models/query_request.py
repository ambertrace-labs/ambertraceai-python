from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_request_facts_type_0 import QueryRequestFactsType0
    from ..models.query_request_predictions_type_0 import QueryRequestPredictionsType0
    from ..models.query_request_relations_type_0 import QueryRequestRelationsType0


T = TypeVar("T", bound="QueryRequest")


@_attrs_define
class QueryRequest:
    """
    Attributes:
        query (str):
        explain (bool | Unset):  Default: True.
        facts (None | QueryRequestFactsType0 | Unset): Optional structured request facts as a {field: scalar} map. When
            supplied to a verified platform, these ARE the certified EDB — each fact is certified through the same gate
            (declared in the domain schema, in-domain, ground) and neural retrieval is NOT consulted for the fact base, so a
            fully-specified request decides deterministically. Use for policy-decision-point callers that hold the request
            attributes (the request IS the facts); the natural-language `query` then drives only the answer narrative.
            Undeclared or out-of-domain fields are rejected, surfaced in the 503 details.
        predictions (None | QueryRequestPredictionsType0 | Unset): Optional VERIFIED-PREDICTION REFERENCES as a {role:
            {model_id, as_of}} map (the Prediction -> Decision Bridge fan-in). Each role names a persisted PredictionRecord
            the PLATFORM produced+stored — the caller references it by id + alignment period, NEVER supplying the forecast
            value (which the platform does not trust: the forecast's certificate certifies its INPUT ROW, not the emitted
            value). The platform fetches the SCOPED (org+owner) stored record and admits its certified fields to the
            decision's certified EDB keyed `<role>.<field>`: `<role>.value`, `<role>.probability` (only if the record's
            probability certified), and `<role>.fired.<signal>` per fired signal. A rule reading `<role>.<field>` then
            decides over trusted facts. FAIL-CLOSED (WS4): a reference that is missing / not proof_checked / whose as_of !=
            the requested as_of / (for probability) not probability_certified admits NO fact, so a rule reading it cannot
            fire a certified permit and the decision abstains. `proof_checked=True` iff the decision certifies AND every
            referenced prediction was found+aligned+certified. Verified platforms only. Example: {"ust_10y": {"model_id":
            "ust_10y", "as_of": "2026-06-30"}}.
        relations (None | QueryRequestRelationsType0 | Unset): Optional ATTACHED RELATED FACTS as a {relation_name:
            [row, ...]} map, where each row is a {column: scalar} dict. These ride alongside the focal `facts` (the scalar
            row, including any join-key column) and let the verified kernel bring a relational/cross-domain join INSIDE the
            proof: an aggregate (count/sum) or existential (existsRelated — DIANA Tier-1 cross-domain cueing) derive rule
            folds over the certified related rows, joined on the declared join key, and its derived flag feeds the decision.
            Every row is certified per-cell through the same fact gate at the platform's confidence threshold; if ANY row is
            rejected the whole query fails CLOSED (no decision over a partial relation). Verified platforms only.
        top_k (int | Unset):  Default: 10.
    """

    query: str
    explain: bool | Unset = True
    facts: None | QueryRequestFactsType0 | Unset = UNSET
    predictions: None | QueryRequestPredictionsType0 | Unset = UNSET
    relations: None | QueryRequestRelationsType0 | Unset = UNSET
    top_k: int | Unset = 10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_request_facts_type_0 import QueryRequestFactsType0
        from ..models.query_request_predictions_type_0 import (
            QueryRequestPredictionsType0,
        )
        from ..models.query_request_relations_type_0 import QueryRequestRelationsType0

        query = self.query

        explain = self.explain

        facts: dict[str, Any] | None | Unset
        if isinstance(self.facts, Unset):
            facts = UNSET
        elif isinstance(self.facts, QueryRequestFactsType0):
            facts = self.facts.to_dict()
        else:
            facts = self.facts

        predictions: dict[str, Any] | None | Unset
        if isinstance(self.predictions, Unset):
            predictions = UNSET
        elif isinstance(self.predictions, QueryRequestPredictionsType0):
            predictions = self.predictions.to_dict()
        else:
            predictions = self.predictions

        relations: dict[str, Any] | None | Unset
        if isinstance(self.relations, Unset):
            relations = UNSET
        elif isinstance(self.relations, QueryRequestRelationsType0):
            relations = self.relations.to_dict()
        else:
            relations = self.relations

        top_k = self.top_k

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if explain is not UNSET:
            field_dict["explain"] = explain
        if facts is not UNSET:
            field_dict["facts"] = facts
        if predictions is not UNSET:
            field_dict["predictions"] = predictions
        if relations is not UNSET:
            field_dict["relations"] = relations
        if top_k is not UNSET:
            field_dict["top_k"] = top_k

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_request_facts_type_0 import QueryRequestFactsType0
        from ..models.query_request_predictions_type_0 import (
            QueryRequestPredictionsType0,
        )
        from ..models.query_request_relations_type_0 import QueryRequestRelationsType0

        d = dict(src_dict)
        query = d.pop("query")

        explain = d.pop("explain", UNSET)

        def _parse_facts(data: object) -> None | QueryRequestFactsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                facts_type_0 = QueryRequestFactsType0.from_dict(data)

                return facts_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QueryRequestFactsType0 | Unset, data)

        facts = _parse_facts(d.pop("facts", UNSET))

        def _parse_predictions(
            data: object,
        ) -> None | QueryRequestPredictionsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                predictions_type_0 = QueryRequestPredictionsType0.from_dict(data)

                return predictions_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QueryRequestPredictionsType0 | Unset, data)

        predictions = _parse_predictions(d.pop("predictions", UNSET))

        def _parse_relations(data: object) -> None | QueryRequestRelationsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                relations_type_0 = QueryRequestRelationsType0.from_dict(data)

                return relations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QueryRequestRelationsType0 | Unset, data)

        relations = _parse_relations(d.pop("relations", UNSET))

        top_k = d.pop("top_k", UNSET)

        query_request = cls(
            query=query,
            explain=explain,
            facts=facts,
            predictions=predictions,
            relations=relations,
            top_k=top_k,
        )

        query_request.additional_properties = d
        return query_request

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
