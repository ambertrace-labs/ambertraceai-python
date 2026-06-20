from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.fetch_source import FetchSource


T = TypeVar("T", bound="DatasetFetchMultiRequest")


@_attrs_define
class DatasetFetchMultiRequest:
    """
    Attributes:
        domain_id (int):
        sources (list[FetchSource]): Two or more connector sources to fetch and merge into one dataset. Each value
            column is namespaced by connector_type (e.g. boe.IUDSOIA).
        aggregation (str | Unset): Resample aggregation when frequency is set: 'last' or 'mean'. Default: 'last'.
        frequency (None | str | Unset): Optional common grid to resample every source onto before joining: daily,
            weekly, monthly, quarterly, or annual. Without it, mixed-frequency sources outer-join to a mostly-null table.
        join_on (str | Unset): Index column to outer-join the sources on (default 'date'). Default: 'date'.
    """

    domain_id: int
    sources: list[FetchSource]
    aggregation: str | Unset = "last"
    frequency: None | str | Unset = UNSET
    join_on: str | Unset = "date"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        sources = []
        for sources_item_data in self.sources:
            sources_item = sources_item_data.to_dict()
            sources.append(sources_item)

        aggregation = self.aggregation

        frequency: None | str | Unset
        if isinstance(self.frequency, Unset):
            frequency = UNSET
        else:
            frequency = self.frequency

        join_on = self.join_on

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "sources": sources,
            }
        )
        if aggregation is not UNSET:
            field_dict["aggregation"] = aggregation
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if join_on is not UNSET:
            field_dict["join_on"] = join_on

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.fetch_source import FetchSource

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        sources = []
        _sources = d.pop("sources")
        for sources_item_data in _sources:
            sources_item = FetchSource.from_dict(sources_item_data)

            sources.append(sources_item)

        aggregation = d.pop("aggregation", UNSET)

        def _parse_frequency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        frequency = _parse_frequency(d.pop("frequency", UNSET))

        join_on = d.pop("join_on", UNSET)

        dataset_fetch_multi_request = cls(
            domain_id=domain_id,
            sources=sources,
            aggregation=aggregation,
            frequency=frequency,
            join_on=join_on,
        )

        dataset_fetch_multi_request.additional_properties = d
        return dataset_fetch_multi_request

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
