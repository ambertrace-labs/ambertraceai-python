from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.edge_out_properties_type_0 import EdgeOutPropertiesType0


T = TypeVar("T", bound="EdgeOut")


@_attrs_define
class EdgeOut:
    """
    Attributes:
        source_uuid (str):
        target_uuid (str):
        edge_uuid (None | str | Unset):
        properties (EdgeOutPropertiesType0 | None | Unset):
        relation_type (None | str | Unset):
    """

    source_uuid: str
    target_uuid: str
    edge_uuid: None | str | Unset = UNSET
    properties: EdgeOutPropertiesType0 | None | Unset = UNSET
    relation_type: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.edge_out_properties_type_0 import EdgeOutPropertiesType0

        source_uuid = self.source_uuid

        target_uuid = self.target_uuid

        edge_uuid: None | str | Unset
        if isinstance(self.edge_uuid, Unset):
            edge_uuid = UNSET
        else:
            edge_uuid = self.edge_uuid

        properties: dict[str, Any] | None | Unset
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, EdgeOutPropertiesType0):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        relation_type: None | str | Unset
        if isinstance(self.relation_type, Unset):
            relation_type = UNSET
        else:
            relation_type = self.relation_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "source_uuid": source_uuid,
                "target_uuid": target_uuid,
            }
        )
        if edge_uuid is not UNSET:
            field_dict["edge_uuid"] = edge_uuid
        if properties is not UNSET:
            field_dict["properties"] = properties
        if relation_type is not UNSET:
            field_dict["relation_type"] = relation_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.edge_out_properties_type_0 import EdgeOutPropertiesType0

        d = dict(src_dict)
        source_uuid = d.pop("source_uuid")

        target_uuid = d.pop("target_uuid")

        def _parse_edge_uuid(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        edge_uuid = _parse_edge_uuid(d.pop("edge_uuid", UNSET))

        def _parse_properties(data: object) -> EdgeOutPropertiesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = EdgeOutPropertiesType0.from_dict(data)

                return properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EdgeOutPropertiesType0 | None | Unset, data)

        properties = _parse_properties(d.pop("properties", UNSET))

        def _parse_relation_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        relation_type = _parse_relation_type(d.pop("relation_type", UNSET))

        edge_out = cls(
            source_uuid=source_uuid,
            target_uuid=target_uuid,
            edge_uuid=edge_uuid,
            properties=properties,
            relation_type=relation_type,
        )

        edge_out.additional_properties = d
        return edge_out

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
