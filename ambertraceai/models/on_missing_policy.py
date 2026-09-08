from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.on_missing_policy_per_column_type_0 import OnMissingPolicyPerColumnType0


T = TypeVar("T", bound="OnMissingPolicy")


@_attrs_define
class OnMissingPolicy:
    """Customer-declared missing-value policy for multi-source panels.

    Controls how NaN cells in the outer-joined panel are handled.

        Attributes:
            max_gap (int | Unset): Maximum contiguous NaN gap eligible for interpolation (only used when
                method='interpolate'). Gaps longer than this are NOT interpolated -- those rows are dropped. Default 3. Default:
                3.
            method (str | Unset): How to handle missing values after the outer join. 'drop' -- drop rows with any NaN (no
                fill). 'ffill' -- forward-fill (last observation carried forward; default). 'interpolate' -- linear
                interpolation for short gaps (up to max_gap contiguous NaN); longer gaps are dropped. 'proxy_splice' -- forward-
                fill + back-fill to splice proxy series; flagged as modeled_extrapolation in the transformation manifest.
                Default: 'ffill'.
            per_column (None | OnMissingPolicyPerColumnType0 | Unset): Per-source periodicity override: column name (POST-
                NAMESPACE, e.g. 'boe__IUDSOIA') -> {method, max_gap}. Overrides the top-level method/max_gap for the named
                columns ONLY; every other value column keeps the top-level method. E.g. mix ffill for a step-function rate
                series with interpolate for a smooth curve series in the SAME panel. The transformation manifest records the
                ACTUAL per-column method used, not merely the top-level default.
    """

    max_gap: int | Unset = 3
    method: str | Unset = "ffill"
    per_column: None | OnMissingPolicyPerColumnType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.on_missing_policy_per_column_type_0 import OnMissingPolicyPerColumnType0

        max_gap = self.max_gap

        method = self.method

        per_column: dict[str, Any] | None | Unset
        if isinstance(self.per_column, Unset):
            per_column = UNSET
        elif isinstance(self.per_column, OnMissingPolicyPerColumnType0):
            per_column = self.per_column.to_dict()
        else:
            per_column = self.per_column

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if max_gap is not UNSET:
            field_dict["max_gap"] = max_gap
        if method is not UNSET:
            field_dict["method"] = method
        if per_column is not UNSET:
            field_dict["per_column"] = per_column

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.on_missing_policy_per_column_type_0 import OnMissingPolicyPerColumnType0

        d = dict(src_dict)
        max_gap = d.pop("max_gap", UNSET)

        method = d.pop("method", UNSET)

        def _parse_per_column(data: object) -> None | OnMissingPolicyPerColumnType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                per_column_type_0 = OnMissingPolicyPerColumnType0.from_dict(data)

                return per_column_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | OnMissingPolicyPerColumnType0 | Unset, data)

        per_column = _parse_per_column(d.pop("per_column", UNSET))

        on_missing_policy = cls(
            max_gap=max_gap,
            method=method,
            per_column=per_column,
        )

        on_missing_policy.additional_properties = d
        return on_missing_policy

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
