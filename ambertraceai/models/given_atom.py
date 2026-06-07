from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="GivenAtom")


@_attrs_define
class GivenAtom:
    """A value-bound witness entry for a ``require`` invariant.

    Binds a concrete ground scalar to a field in the witness base, so the
    obligation can witness conjunction / set / enum / numeric classifiers
    (e.g. ``device_posture_score = 85`` satisfying ``posture >= 70``) and
    drive multi-hop conclusion atoms through the whole rule chain.

        Attributes:
            field (str): The input/derived field name to bind.
            value (bool | float | int | str): The ground scalar value the witness assigns to the field.
    """

    field: str
    value: bool | float | int | str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        value: bool | float | int | str
        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "value": value,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        def _parse_value(data: object) -> bool | float | int | str:
            return cast(bool | float | int | str, data)

        value = _parse_value(d.pop("value"))

        given_atom = cls(
            field=field,
            value=value,
        )

        given_atom.additional_properties = d
        return given_atom

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
