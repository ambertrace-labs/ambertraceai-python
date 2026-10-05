from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VerifyPropertyVariable")


@_attrs_define
class VerifyPropertyVariable:
    """One axis of a regime grid (``exactly_one_verdict``).

    Attributes:
        domain (list[bool | int | str]): The finite, explicit value domain of the field (distinct discrete values).
        field (str): The rule-condition field this axis ranges over (alphanumeric/underscore).
    """

    domain: list[bool | int | str]
    field: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain = []
        for domain_item_data in self.domain:
            domain_item: bool | int | str
            domain_item = domain_item_data
            domain.append(domain_item)

        field = self.field

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain": domain,
                "field": field,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        domain = []
        _domain = d.pop("domain")
        for domain_item_data in _domain:

            def _parse_domain_item(data: object) -> bool | int | str:
                return cast(bool | int | str, data)

            domain_item = _parse_domain_item(domain_item_data)

            domain.append(domain_item)

        field = d.pop("field")

        verify_property_variable = cls(
            domain=domain,
            field=field,
        )

        verify_property_variable.additional_properties = d
        return verify_property_variable

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
