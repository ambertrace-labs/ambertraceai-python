from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.replay_metric import ReplayMetric
    from ..models.replay_result_row_details_item import ReplayResultRowDetailsItem


T = TypeVar("T", bound="ReplayResult")


@_attrs_define
class ReplayResult:
    """
    Attributes:
        fire_rate (float):
        fired_rows (int):
        rule_name (str):
        total_rows (int):
        metric (None | ReplayMetric | Unset):
        row_details (list[ReplayResultRowDetailsItem] | Unset):
    """

    fire_rate: float
    fired_rows: int
    rule_name: str
    total_rows: int
    metric: None | ReplayMetric | Unset = UNSET
    row_details: list[ReplayResultRowDetailsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.replay_metric import ReplayMetric

        fire_rate = self.fire_rate

        fired_rows = self.fired_rows

        rule_name = self.rule_name

        total_rows = self.total_rows

        metric: dict[str, Any] | None | Unset
        if isinstance(self.metric, Unset):
            metric = UNSET
        elif isinstance(self.metric, ReplayMetric):
            metric = self.metric.to_dict()
        else:
            metric = self.metric

        row_details: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.row_details, Unset):
            row_details = []
            for row_details_item_data in self.row_details:
                row_details_item = row_details_item_data.to_dict()
                row_details.append(row_details_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "fire_rate": fire_rate,
                "fired_rows": fired_rows,
                "rule_name": rule_name,
                "total_rows": total_rows,
            }
        )
        if metric is not UNSET:
            field_dict["metric"] = metric
        if row_details is not UNSET:
            field_dict["row_details"] = row_details

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.replay_metric import ReplayMetric
        from ..models.replay_result_row_details_item import ReplayResultRowDetailsItem

        d = dict(src_dict)
        fire_rate = d.pop("fire_rate")

        fired_rows = d.pop("fired_rows")

        rule_name = d.pop("rule_name")

        total_rows = d.pop("total_rows")

        def _parse_metric(data: object) -> None | ReplayMetric | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metric_type_0 = ReplayMetric.from_dict(data)

                return metric_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | ReplayMetric | Unset, data)

        metric = _parse_metric(d.pop("metric", UNSET))

        _row_details = d.pop("row_details", UNSET)
        row_details: list[ReplayResultRowDetailsItem] | Unset = UNSET
        if _row_details is not UNSET:
            row_details = []
            for row_details_item_data in _row_details:
                row_details_item = ReplayResultRowDetailsItem.from_dict(
                    row_details_item_data
                )

                row_details.append(row_details_item)

        replay_result = cls(
            fire_rate=fire_rate,
            fired_rows=fired_rows,
            rule_name=rule_name,
            total_rows=total_rows,
            metric=metric,
            row_details=row_details,
        )

        replay_result.additional_properties = d
        return replay_result

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
