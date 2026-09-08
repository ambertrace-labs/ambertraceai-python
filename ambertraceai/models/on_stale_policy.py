from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.on_stale_policy_action import OnStalePolicyAction
from ..types import UNSET, Unset

T = TypeVar("T", bound="OnStalePolicy")


@_attrs_define
class OnStalePolicy:
    """Customer-declared staleness policy for multi-source panels.

    Controls what happens when a source column's last non-null value lags the
    panel's last index by more than ``stale_periods`` cadence periods (i.e. it
    is flagged stale by the panel sufficiency report).

        Attributes:
            action (OnStalePolicyAction | Unset): How to handle stale columns after the merge. 'warn' -- proceed; staleness
                is recorded in the panel sufficiency report but does not block (default, current behaviour). 'error' -- mark the
                dataset as error if any column is stale (fail-closed; the error message names the stale columns). 'drop_columns'
                -- drop stale columns from the merged frame, re-derive schema and panel sufficiency, and record the dropped
                columns as dropped_stale_columns on schema_info. Default: OnStalePolicyAction.WARN.
            stale_periods (int | Unset): A column is flagged stale when its last non-null value lags the panel's last index
                by MORE than this many cadence periods (cadence = median index spacing). Overrides the default stale_periods=3
                used by the panel sufficiency computation. Default: 3.
    """

    action: OnStalePolicyAction | Unset = OnStalePolicyAction.WARN
    stale_periods: int | Unset = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action: str | Unset = UNSET
        if not isinstance(self.action, Unset):
            action = self.action.value

        stale_periods = self.stale_periods

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action is not UNSET:
            field_dict["action"] = action
        if stale_periods is not UNSET:
            field_dict["stale_periods"] = stale_periods

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _action = d.pop("action", UNSET)
        action: OnStalePolicyAction | Unset
        if isinstance(_action, Unset):
            action = UNSET
        else:
            action = OnStalePolicyAction(_action)

        stale_periods = d.pop("stale_periods", UNSET)

        on_stale_policy = cls(
            action=action,
            stale_periods=stale_periods,
        )

        on_stale_policy.additional_properties = d
        return on_stale_policy

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
