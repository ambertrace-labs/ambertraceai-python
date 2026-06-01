from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplayRequest")


@_attrs_define
class ReplayRequest:
    """
    Attributes:
        rule_id (int):
        dataset_id (int | None | Unset):
        include_row_details (bool | Unset):  Default: False.
    """

    rule_id: int
    dataset_id: int | None | Unset = UNSET
    include_row_details: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rule_id = self.rule_id

        dataset_id: int | None | Unset
        if isinstance(self.dataset_id, Unset):
            dataset_id = UNSET
        else:
            dataset_id = self.dataset_id

        include_row_details = self.include_row_details

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rule_id": rule_id,
            }
        )
        if dataset_id is not UNSET:
            field_dict["dataset_id"] = dataset_id
        if include_row_details is not UNSET:
            field_dict["include_row_details"] = include_row_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        rule_id = d.pop("rule_id")

        def _parse_dataset_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        dataset_id = _parse_dataset_id(d.pop("dataset_id", UNSET))

        include_row_details = d.pop("include_row_details", UNSET)

        replay_request = cls(
            rule_id=rule_id,
            dataset_id=dataset_id,
            include_row_details=include_row_details,
        )

        replay_request.additional_properties = d
        return replay_request

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
