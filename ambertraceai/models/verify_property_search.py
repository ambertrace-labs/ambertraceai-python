from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyPropertySearch")


@_attrs_define
class VerifyPropertySearch:
    """
    Attributes:
        complete (bool): True iff the checker attests its enumeration covered ALL of S (HOLDS). False for VIOLATED
            (stopped at the first counterexample) and ABSTAIN.
        bound (int | None | Unset): The bound you declared.
        space_size (int | None | Unset): |S| = product of the declared domain sizes (hand-checkable). On HOLDS this is
            the figure the proven checker itself recomputed; null only when the request was rejected before a space could be
            built.
    """

    complete: bool
    bound: int | None | Unset = UNSET
    space_size: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        complete = self.complete

        bound: int | None | Unset
        if isinstance(self.bound, Unset):
            bound = UNSET
        else:
            bound = self.bound

        space_size: int | None | Unset
        if isinstance(self.space_size, Unset):
            space_size = UNSET
        else:
            space_size = self.space_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "complete": complete,
            }
        )
        if bound is not UNSET:
            field_dict["bound"] = bound
        if space_size is not UNSET:
            field_dict["space_size"] = space_size

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        complete = d.pop("complete")

        def _parse_bound(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        bound = _parse_bound(d.pop("bound", UNSET))

        def _parse_space_size(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        space_size = _parse_space_size(d.pop("space_size", UNSET))

        verify_property_search = cls(
            complete=complete,
            bound=bound,
            space_size=space_size,
        )

        verify_property_search.additional_properties = d
        return verify_property_search

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
