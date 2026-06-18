from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SchemaReconciliationConflict")


@_attrs_define
class SchemaReconciliationConflict:
    """A field reference that could not be mapped to any data column.

    Attributes:
        field (str): The unmappable field reference.
        reason (str): Why it could not be mapped.
        rule (str): Name of the offending rule.
        candidates (list[str] | Unset): Nearby column names considered, if any.
    """

    field: str
    reason: str
    rule: str
    candidates: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        reason = self.reason

        rule = self.rule

        candidates: list[str] | Unset = UNSET
        if not isinstance(self.candidates, Unset):
            candidates = self.candidates

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "reason": reason,
                "rule": rule,
            }
        )
        if candidates is not UNSET:
            field_dict["candidates"] = candidates

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        reason = d.pop("reason")

        rule = d.pop("rule")

        candidates = cast(list[str], d.pop("candidates", UNSET))

        schema_reconciliation_conflict = cls(
            field=field,
            reason=reason,
            rule=rule,
            candidates=candidates,
        )

        schema_reconciliation_conflict.additional_properties = d
        return schema_reconciliation_conflict

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
