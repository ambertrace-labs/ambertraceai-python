from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PanelColumnOut")


@_attrs_define
class PanelColumnOut:
    """
    Attributes:
        name (str):
        first_non_null (None | str | Unset):
        last_non_null (None | str | Unset):
        non_null_count (int | Unset):  Default: 0.
        null_count (int | Unset):  Default: 0.
        recency_lag_periods (int | None | Unset):
        role (None | str | Unset): Column role: 'core' or 'auxiliary'. Only populated when the caller passed
            column_roles (or the ingested dataset carries a schema_info['column_roles'] declaration); None when no role
            declaration exists for this panel.
        rows_recovered_if_dropped (int | Unset):  Default: 0.
        stale (bool | Unset):  Default: False.
    """

    name: str
    first_non_null: None | str | Unset = UNSET
    last_non_null: None | str | Unset = UNSET
    non_null_count: int | Unset = 0
    null_count: int | Unset = 0
    recency_lag_periods: int | None | Unset = UNSET
    role: None | str | Unset = UNSET
    rows_recovered_if_dropped: int | Unset = 0
    stale: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        first_non_null: None | str | Unset
        if isinstance(self.first_non_null, Unset):
            first_non_null = UNSET
        else:
            first_non_null = self.first_non_null

        last_non_null: None | str | Unset
        if isinstance(self.last_non_null, Unset):
            last_non_null = UNSET
        else:
            last_non_null = self.last_non_null

        non_null_count = self.non_null_count

        null_count = self.null_count

        recency_lag_periods: int | None | Unset
        if isinstance(self.recency_lag_periods, Unset):
            recency_lag_periods = UNSET
        else:
            recency_lag_periods = self.recency_lag_periods

        role: None | str | Unset
        if isinstance(self.role, Unset):
            role = UNSET
        else:
            role = self.role

        rows_recovered_if_dropped = self.rows_recovered_if_dropped

        stale = self.stale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if first_non_null is not UNSET:
            field_dict["first_non_null"] = first_non_null
        if last_non_null is not UNSET:
            field_dict["last_non_null"] = last_non_null
        if non_null_count is not UNSET:
            field_dict["non_null_count"] = non_null_count
        if null_count is not UNSET:
            field_dict["null_count"] = null_count
        if recency_lag_periods is not UNSET:
            field_dict["recency_lag_periods"] = recency_lag_periods
        if role is not UNSET:
            field_dict["role"] = role
        if rows_recovered_if_dropped is not UNSET:
            field_dict["rows_recovered_if_dropped"] = rows_recovered_if_dropped
        if stale is not UNSET:
            field_dict["stale"] = stale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        def _parse_first_non_null(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        first_non_null = _parse_first_non_null(d.pop("first_non_null", UNSET))

        def _parse_last_non_null(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        last_non_null = _parse_last_non_null(d.pop("last_non_null", UNSET))

        non_null_count = d.pop("non_null_count", UNSET)

        null_count = d.pop("null_count", UNSET)

        def _parse_recency_lag_periods(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        recency_lag_periods = _parse_recency_lag_periods(d.pop("recency_lag_periods", UNSET))

        def _parse_role(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        role = _parse_role(d.pop("role", UNSET))

        rows_recovered_if_dropped = d.pop("rows_recovered_if_dropped", UNSET)

        stale = d.pop("stale", UNSET)

        panel_column_out = cls(
            name=name,
            first_non_null=first_non_null,
            last_non_null=last_non_null,
            non_null_count=non_null_count,
            null_count=null_count,
            recency_lag_periods=recency_lag_periods,
            role=role,
            rows_recovered_if_dropped=rows_recovered_if_dropped,
            stale=stale,
        )

        panel_column_out.additional_properties = d
        return panel_column_out

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
