from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PruneDraftsRequest")


@_attrs_define
class PruneDraftsRequest:
    """
    Attributes:
        older_than_days (int): Reap abandoned draft domains created more than this many days ago (0 = every abandoned
            draft).
    """

    older_than_days: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        older_than_days = self.older_than_days

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "older_than_days": older_than_days,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        older_than_days = d.pop("older_than_days")

        prune_drafts_request = cls(
            older_than_days=older_than_days,
        )

        prune_drafts_request.additional_properties = d
        return prune_drafts_request

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
