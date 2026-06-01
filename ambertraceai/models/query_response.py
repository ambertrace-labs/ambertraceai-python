from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.query_response_explanation_type_0 import QueryResponseExplanationType0


T = TypeVar("T", bound="QueryResponse")


@_attrs_define
class QueryResponse:
    """
    Attributes:
        answer (str):
        platform_id (int):
        query (str):
        explanation (None | QueryResponseExplanationType0 | Unset):
    """

    answer: str
    platform_id: int
    query: str
    explanation: None | QueryResponseExplanationType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.query_response_explanation_type_0 import (
            QueryResponseExplanationType0,
        )

        answer = self.answer

        platform_id = self.platform_id

        query = self.query

        explanation: dict[str, Any] | None | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        elif isinstance(self.explanation, QueryResponseExplanationType0):
            explanation = self.explanation.to_dict()
        else:
            explanation = self.explanation

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "answer": answer,
                "platform_id": platform_id,
                "query": query,
            }
        )
        if explanation is not UNSET:
            field_dict["explanation"] = explanation

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.query_response_explanation_type_0 import (
            QueryResponseExplanationType0,
        )

        d = dict(src_dict)
        answer = d.pop("answer")

        platform_id = d.pop("platform_id")

        query = d.pop("query")

        def _parse_explanation(
            data: object,
        ) -> None | QueryResponseExplanationType0 | Unset:
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

        query_response = cls(
            answer=answer,
            platform_id=platform_id,
            query=query,
            explanation=explanation,
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
