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
        proof_checked (bool | None | Unset): Verified profile only. ``True`` when the decision was independently re-
            derived and verified (the active rule set satisfies the platform's invariant manifest and the proof certificate
            is valid). ``null`` for non-verified platforms (no proof is generated). A verified query that cannot be
            certified returns HTTP 503 rather than ``proof_checked: false``.
        proof_summary (None | str | Unset): Human-readable summary of the machine-checked certificate (rules fired,
            facts derived, input facts). ``null`` for non-verified platforms. The full derivation proof and any
            ``rejected_facts`` are in ``explanation.proof`` / ``explanation.rejected_facts``.
    """

    answer: str
    platform_id: int
    query: str
    explanation: None | QueryResponseExplanationType0 | Unset = UNSET
    proof_checked: bool | None | Unset = UNSET
    proof_summary: None | str | Unset = UNSET
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
        if proof_checked is not UNSET:
            field_dict["proof_checked"] = proof_checked
        if proof_summary is not UNSET:
            field_dict["proof_summary"] = proof_summary

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

        query_response = cls(
            answer=answer,
            platform_id=platform_id,
            query=query,
            explanation=explanation,
            proof_checked=proof_checked,
            proof_summary=proof_summary,
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
