from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DecisionTableRowIn")


@_attrs_define
class DecisionTableRowIn:
    """
    Attributes:
        label (str): The customer's word for this outcome, served as written. Unique (case-insensitive); not 'derive' or
            a numeric-action word.
        default (bool | None | Unset): Ladder only: the outcome when nothing fires. Exactly one row.
        id (None | str | Unset): System-minted row id ('o1', 'o2', ...). Omit on a new row; send it back on an edit to
            keep the row's id stable.
        order (int | None | Unset): Ladder only: precedence among fired outcomes; higher wins. Distinct.
        permits (bool | None | Unset): Ladder only: may the action proceed. Omitted -> order <= order(default row).
        values (list[str] | None | Unset): Data cells that denote this row when they differ from the label (exact, case-
            insensitive match).
    """

    label: str
    default: bool | None | Unset = UNSET
    id: None | str | Unset = UNSET
    order: int | None | Unset = UNSET
    permits: bool | None | Unset = UNSET
    values: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        label = self.label

        default: bool | None | Unset
        if isinstance(self.default, Unset):
            default = UNSET
        else:
            default = self.default

        id: None | str | Unset
        if isinstance(self.id, Unset):
            id = UNSET
        else:
            id = self.id

        order: int | None | Unset
        if isinstance(self.order, Unset):
            order = UNSET
        else:
            order = self.order

        permits: bool | None | Unset
        if isinstance(self.permits, Unset):
            permits = UNSET
        else:
            permits = self.permits

        values: list[str] | None | Unset
        if isinstance(self.values, Unset):
            values = UNSET
        elif isinstance(self.values, list):
            values = self.values

        else:
            values = self.values

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "label": label,
            }
        )
        if default is not UNSET:
            field_dict["default"] = default
        if id is not UNSET:
            field_dict["id"] = id
        if order is not UNSET:
            field_dict["order"] = order
        if permits is not UNSET:
            field_dict["permits"] = permits
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        label = d.pop("label")

        def _parse_default(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        default = _parse_default(d.pop("default", UNSET))

        def _parse_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        id = _parse_id(d.pop("id", UNSET))

        def _parse_order(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        order = _parse_order(d.pop("order", UNSET))

        def _parse_permits(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        permits = _parse_permits(d.pop("permits", UNSET))

        def _parse_values(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                values_type_0 = cast(list[str], data)

                return values_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        values = _parse_values(d.pop("values", UNSET))

        decision_table_row_in = cls(
            label=label,
            default=default,
            id=id,
            order=order,
            permits=permits,
            values=values,
        )

        decision_table_row_in.additional_properties = d
        return decision_table_row_in

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
