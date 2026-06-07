from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.drift_baseline_out_per_rule_fire_rate import (
        DriftBaselineOutPerRuleFireRate,
    )


T = TypeVar("T", bound="DriftBaselineOut")


@_attrs_define
class DriftBaselineOut:
    """Approval-time drift baseline captured for a platform.

    Attributes:
        certified_rejection_rate (float):
        n (int):
        per_rule_fire_rate (DriftBaselineOutPerRuleFireRate):
        platform_id (int):
        captured_at (None | str | Unset):
    """

    certified_rejection_rate: float
    n: int
    per_rule_fire_rate: DriftBaselineOutPerRuleFireRate
    platform_id: int
    captured_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        certified_rejection_rate = self.certified_rejection_rate

        n = self.n

        per_rule_fire_rate = self.per_rule_fire_rate.to_dict()

        platform_id = self.platform_id

        captured_at: None | str | Unset
        if isinstance(self.captured_at, Unset):
            captured_at = UNSET
        else:
            captured_at = self.captured_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "certified_rejection_rate": certified_rejection_rate,
                "n": n,
                "per_rule_fire_rate": per_rule_fire_rate,
                "platform_id": platform_id,
            }
        )
        if captured_at is not UNSET:
            field_dict["captured_at"] = captured_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.drift_baseline_out_per_rule_fire_rate import (
            DriftBaselineOutPerRuleFireRate,
        )

        d = dict(src_dict)
        certified_rejection_rate = d.pop("certified_rejection_rate")

        n = d.pop("n")

        per_rule_fire_rate = DriftBaselineOutPerRuleFireRate.from_dict(
            d.pop("per_rule_fire_rate")
        )

        platform_id = d.pop("platform_id")

        def _parse_captured_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        captured_at = _parse_captured_at(d.pop("captured_at", UNSET))

        drift_baseline_out = cls(
            certified_rejection_rate=certified_rejection_rate,
            n=n,
            per_rule_fire_rate=per_rule_fire_rate,
            platform_id=platform_id,
            captured_at=captured_at,
        )

        drift_baseline_out.additional_properties = d
        return drift_baseline_out

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
