from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VersionData")


@_attrs_define
class VersionData:
    """
    Attributes:
        built_at (str):
        git_sha (str):
        version (str):
    """

    built_at: str
    git_sha: str
    version: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        built_at = self.built_at

        git_sha = self.git_sha

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "built_at": built_at,
                "git_sha": git_sha,
                "version": version,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        built_at = d.pop("built_at")

        git_sha = d.pop("git_sha")

        version = d.pop("version")

        version_data = cls(
            built_at=built_at,
            git_sha=git_sha,
            version=version,
        )

        version_data.additional_properties = d
        return version_data

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
