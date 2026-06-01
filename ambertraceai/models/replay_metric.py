from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ReplayMetric")


@_attrs_define
class ReplayMetric:
    """
    Attributes:
        after (float | None | Unset):
        before (float | None | Unset):
        delta (float | None | Unset):
        direction (None | str | Unset):
        field (None | str | Unset):
    """

    after: float | None | Unset = UNSET
    before: float | None | Unset = UNSET
    delta: float | None | Unset = UNSET
    direction: None | str | Unset = UNSET
    field: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        after: float | None | Unset
        if isinstance(self.after, Unset):
            after = UNSET
        else:
            after = self.after

        before: float | None | Unset
        if isinstance(self.before, Unset):
            before = UNSET
        else:
            before = self.before

        delta: float | None | Unset
        if isinstance(self.delta, Unset):
            delta = UNSET
        else:
            delta = self.delta

        direction: None | str | Unset
        if isinstance(self.direction, Unset):
            direction = UNSET
        else:
            direction = self.direction

        field: None | str | Unset
        if isinstance(self.field, Unset):
            field = UNSET
        else:
            field = self.field

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if after is not UNSET:
            field_dict["after"] = after
        if before is not UNSET:
            field_dict["before"] = before
        if delta is not UNSET:
            field_dict["delta"] = delta
        if direction is not UNSET:
            field_dict["direction"] = direction
        if field is not UNSET:
            field_dict["field"] = field

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_after(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        after = _parse_after(d.pop("after", UNSET))

        def _parse_before(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        before = _parse_before(d.pop("before", UNSET))

        def _parse_delta(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        delta = _parse_delta(d.pop("delta", UNSET))

        def _parse_direction(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        direction = _parse_direction(d.pop("direction", UNSET))

        def _parse_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        field = _parse_field(d.pop("field", UNSET))

        replay_metric = cls(
            after=after,
            before=before,
            delta=delta,
            direction=direction,
            field=field,
        )

        replay_metric.additional_properties = d
        return replay_metric

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
