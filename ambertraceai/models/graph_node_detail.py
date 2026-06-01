from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.graph_node_detail_neighbours_item import GraphNodeDetailNeighboursItem
    from ..models.graph_node_detail_properties_type_0 import (
        GraphNodeDetailPropertiesType0,
    )


T = TypeVar("T", bound="GraphNodeDetail")


@_attrs_define
class GraphNodeDetail:
    """
    Attributes:
        node_uuid (str):
        label (None | str | Unset):
        neighbours (list[GraphNodeDetailNeighboursItem] | Unset):
        node_type (None | str | Unset):
        properties (GraphNodeDetailPropertiesType0 | None | Unset):
    """

    node_uuid: str
    label: None | str | Unset = UNSET
    neighbours: list[GraphNodeDetailNeighboursItem] | Unset = UNSET
    node_type: None | str | Unset = UNSET
    properties: GraphNodeDetailPropertiesType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.graph_node_detail_properties_type_0 import (
            GraphNodeDetailPropertiesType0,
        )

        node_uuid = self.node_uuid

        label: None | str | Unset
        if isinstance(self.label, Unset):
            label = UNSET
        else:
            label = self.label

        neighbours: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.neighbours, Unset):
            neighbours = []
            for neighbours_item_data in self.neighbours:
                neighbours_item = neighbours_item_data.to_dict()
                neighbours.append(neighbours_item)

        node_type: None | str | Unset
        if isinstance(self.node_type, Unset):
            node_type = UNSET
        else:
            node_type = self.node_type

        properties: dict[str, Any] | None | Unset
        if isinstance(self.properties, Unset):
            properties = UNSET
        elif isinstance(self.properties, GraphNodeDetailPropertiesType0):
            properties = self.properties.to_dict()
        else:
            properties = self.properties

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "node_uuid": node_uuid,
            }
        )
        if label is not UNSET:
            field_dict["label"] = label
        if neighbours is not UNSET:
            field_dict["neighbours"] = neighbours
        if node_type is not UNSET:
            field_dict["node_type"] = node_type
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.graph_node_detail_neighbours_item import (
            GraphNodeDetailNeighboursItem,
        )
        from ..models.graph_node_detail_properties_type_0 import (
            GraphNodeDetailPropertiesType0,
        )

        d = dict(src_dict)
        node_uuid = d.pop("node_uuid")

        def _parse_label(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        label = _parse_label(d.pop("label", UNSET))

        _neighbours = d.pop("neighbours", UNSET)
        neighbours: list[GraphNodeDetailNeighboursItem] | Unset = UNSET
        if _neighbours is not UNSET:
            neighbours = []
            for neighbours_item_data in _neighbours:
                neighbours_item = GraphNodeDetailNeighboursItem.from_dict(
                    neighbours_item_data
                )

                neighbours.append(neighbours_item)

        def _parse_node_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        node_type = _parse_node_type(d.pop("node_type", UNSET))

        def _parse_properties(
            data: object,
        ) -> GraphNodeDetailPropertiesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                properties_type_0 = GraphNodeDetailPropertiesType0.from_dict(data)

                return properties_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(GraphNodeDetailPropertiesType0 | None | Unset, data)

        properties = _parse_properties(d.pop("properties", UNSET))

        graph_node_detail = cls(
            node_uuid=node_uuid,
            label=label,
            neighbours=neighbours,
            node_type=node_type,
            properties=properties,
        )

        graph_node_detail.additional_properties = d
        return graph_node_detail

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
