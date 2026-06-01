from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.relationship_out_properties_type_0 import (
        RelationshipOutPropertiesType0,
    )


T = TypeVar("T", bound="RelationshipOut")


@_attrs_define
class RelationshipOut:
    """
    Attributes:
        domain_id (int):
        id (int):
        relationship_type (str):
        source_entity_id (int):
        target_entity_id (int):
        description (None | str | Unset):
        properties (None | RelationshipOutPropertiesType0 | Unset):
    """

    domain_id: int
    id: int
    relationship_type: str
    source_entity_id: int
    target_entity_id: int
    description: None | str | Unset = UNSET
    properties: None | RelationshipOutPropertiesType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.relationship_out_properties_type_0 import (
            RelationshipOutPropertiesType0,
        )

        domain_id = self.domain_id

        id = self.id

        relationship_type = self.relationship_type

        source_entity_id = self.source_entity_id

        target_entity_id = self.target_entity_id

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        properties: dict[str, Any] | None | Unset
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, RelationshipOutPropertiesType0):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "id": id,
                "relationship_type": relationship_type,
                "source_entity_id": source_entity_id,
                "target_entity_id": target_entity_id,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.relationship_out_properties_type_0 import (
            RelationshipOutPropertiesType0,
        )

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        id = d.pop("id")

        relationship_type = d.pop("relationship_type")

        source_entity_id = d.pop("source_entity_id")

        target_entity_id = d.pop("target_entity_id")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_properties(
            data: object,
        ) -> None | RelationshipOutPropertiesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = RelationshipOutPropertiesType0.from_dict(data)

                return properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RelationshipOutPropertiesType0 | Unset, data)

        properties = _parse_properties(d.pop("properties", UNSET))

        relationship_out = cls(
            domain_id=domain_id,
            id=id,
            relationship_type=relationship_type,
            source_entity_id=source_entity_id,
            target_entity_id=target_entity_id,
            description=description,
            properties=properties,
        )

        relationship_out.additional_properties = d
        return relationship_out

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
