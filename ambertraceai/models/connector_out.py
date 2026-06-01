from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConnectorOut")


@_attrs_define
class ConnectorOut:
    """
    Attributes:
        description (str):
        type_ (str):
        requires (list[str] | Unset):
    """

    description: str
    type_: str
    requires: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        type_ = self.type_

        requires: list[str] | Unset = UNSET
        if not isinstance(self.requires, Unset):
            requires = self.requires

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "type": type_,
            }
        )
        if requires is not UNSET:
            field_dict["requires"] = requires

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        description = d.pop("description")

        type_ = d.pop("type")

        requires = cast(list[str], d.pop("requires", UNSET))

        connector_out = cls(
            description=description,
            type_=type_,
            requires=requires,
        )

        connector_out.additional_properties = d
        return connector_out

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
