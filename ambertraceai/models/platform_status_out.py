from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PlatformStatusOut")


@_attrs_define
class PlatformStatusOut:
    """
    Attributes:
        name (str):
        platform_id (int):
        status (str):
        version (int | Unset):  Default: 1.
    """

    name: str
    platform_id: int
    status: str
    version: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        platform_id = self.platform_id

        status = self.status

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "platform_id": platform_id,
                "status": status,
            }
        )
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        platform_id = d.pop("platform_id")

        status = d.pop("status")

        version = d.pop("version", UNSET)

        platform_status_out = cls(
            name=name,
            platform_id=platform_id,
            status=status,
            version=version,
        )

        platform_status_out.additional_properties = d
        return platform_status_out

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
