from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainSearchOut")


@_attrs_define
class DomainSearchOut:
    """
    Attributes:
        id (int):
        name (str):
        status (str):
        entity_count (int | None | Unset): Ontology entity count; present only with with_entity_count=true.
    """

    id: int
    name: str
    status: str
    entity_count: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        status = self.status

        entity_count: int | None | Unset
        if isinstance(self.entity_count, Unset):
            entity_count = UNSET
        else:
            entity_count = self.entity_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "status": status,
            }
        )
        if entity_count is not UNSET:
            field_dict["entity_count"] = entity_count

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        status = d.pop("status")

        def _parse_entity_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        entity_count = _parse_entity_count(d.pop("entity_count", UNSET))

        domain_search_out = cls(
            id=id,
            name=name,
            status=status,
            entity_count=entity_count,
        )

        domain_search_out.additional_properties = d
        return domain_search_out

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
