from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OnMissingColumnPolicy")


@_attrs_define
class OnMissingColumnPolicy:
    """Per-column override of the on_missing method.

    Lets the customer mix methods within ONE panel -- e.g. ``ffill`` for a
    step-function policy-rate series alongside ``interpolate`` for a smooth
    yield-curve series, matching each source's real periodicity/behaviour.

        Attributes:
            max_gap (int | Unset): Same semantics as OnMissingPolicy.max_gap, for method='interpolate'. Default: 3.
            method (str | Unset): Same accepted values as OnMissingPolicy.method. Default: 'ffill'.
    """

    max_gap: int | Unset = 3
    method: str | Unset = "ffill"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        max_gap = self.max_gap

        method = self.method

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_gap is not UNSET:
            field_dict["max_gap"] = max_gap
        if method is not UNSET:
            field_dict["method"] = method

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        max_gap = d.pop("max_gap", UNSET)

        method = d.pop("method", UNSET)

        on_missing_column_policy = cls(
            max_gap=max_gap,
            method=method,
        )

        on_missing_column_policy.additional_properties = d
        return on_missing_column_policy

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
