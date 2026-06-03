from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.drift_alert import DriftAlert


T = TypeVar("T", bound="DriftCheckOut")


@_attrs_define
class DriftCheckOut:
    """Result of comparing current drift metrics against the stored baseline.

    Attributes:
        platform_id (int):
        alerts (list[DriftAlert] | Unset):
        drift_detected (bool | Unset):  Default: False.
    """

    platform_id: int
    alerts: list[DriftAlert] | Unset = UNSET
    drift_detected: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_id = self.platform_id

        alerts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.alerts, Unset):
            alerts = []
            for alerts_item_data in self.alerts:
                alerts_item = alerts_item_data.to_dict()
                alerts.append(alerts_item)

        drift_detected = self.drift_detected

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_id": platform_id,
            }
        )
        if alerts is not UNSET:
            field_dict["alerts"] = alerts
        if drift_detected is not UNSET:
            field_dict["drift_detected"] = drift_detected

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.drift_alert import DriftAlert

        d = dict(src_dict)
        platform_id = d.pop("platform_id")

        _alerts = d.pop("alerts", UNSET)
        alerts: list[DriftAlert] | Unset = UNSET
        if _alerts is not UNSET:
            alerts = []
            for alerts_item_data in _alerts:
                alerts_item = DriftAlert.from_dict(alerts_item_data)

                alerts.append(alerts_item)

        drift_detected = d.pop("drift_detected", UNSET)

        drift_check_out = cls(
            platform_id=platform_id,
            alerts=alerts,
            drift_detected=drift_detected,
        )

        drift_check_out.additional_properties = d
        return drift_check_out

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
