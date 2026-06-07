from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_request_facts_type_0 import QueryRequestFactsType0


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
        top_k (int | Unset):  Default: 10.
    """

    query: str
    explain: bool | Unset = True
    facts: None | QueryRequestFactsType0 | Unset = UNSET
    top_k: int | Unset = 10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_request_facts_type_0 import QueryRequestFactsType0

        query = self.query

        explain = self.explain

        facts: dict[str, Any] | None | Unset
        if isinstance(self.facts, Unset):
            facts = UNSET
        elif isinstance(self.facts, QueryRequestFactsType0):
            facts = self.facts.to_dict()
        else:
            facts = self.facts

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
        if top_k is not UNSET:
            field_dict["top_k"] = top_k

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_request_facts_type_0 import QueryRequestFactsType0

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

        top_k = d.pop("top_k", UNSET)

        query_request = cls(
            query=query,
            explain=explain,
            facts=facts,
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
