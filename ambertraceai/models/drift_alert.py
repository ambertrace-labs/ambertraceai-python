from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DriftAlert")


@_attrs_define
class DriftAlert:
    """A single drift signal. Shape varies by ``signal`` (see drift_service).

    ``signal == "rule_suppression"`` (ARIA WP5, threat-model A2) additionally
    carries ``severity`` ('silenced' = stopped firing entirely, 'degraded' =
    fire rate collapsed) and the affected ``rule`` name — a previously-active
    safety rule going quiet, surfaced distinctly from generic metric drift.

        Attributes:
            signal (str):
            baseline (float | None | Unset):
            current (float | None | Unset):
            delta (float | None | Unset):
            message (None | str | Unset):
            rule (None | str | Unset):
            severity (None | str | Unset):
    """

    signal: str
    baseline: float | None | Unset = UNSET
    current: float | None | Unset = UNSET
    delta: float | None | Unset = UNSET
    message: None | str | Unset = UNSET
    rule: None | str | Unset = UNSET
    severity: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        signal = self.signal

        baseline: float | None | Unset
        if isinstance(self.baseline, Unset):
            baseline = UNSET
        else:
            baseline = self.baseline

        current: float | None | Unset
        if isinstance(self.current, Unset):
            current = UNSET
        else:
            current = self.current

        delta: float | None | Unset
        if isinstance(self.delta, Unset):
            delta = UNSET
        else:
            delta = self.delta

        message: None | str | Unset
        if isinstance(self.message, Unset):
            message = UNSET
        else:
            message = self.message

        rule: None | str | Unset
        if isinstance(self.rule, Unset):
            rule = UNSET
        else:
            rule = self.rule

        severity: None | str | Unset
        if isinstance(self.severity, Unset):
            severity = UNSET
        else:
            severity = self.severity

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "signal": signal,
            }
        )
        if baseline is not UNSET:
            field_dict["baseline"] = baseline
        if current is not UNSET:
            field_dict["current"] = current
        if delta is not UNSET:
            field_dict["delta"] = delta
        if message is not UNSET:
            field_dict["message"] = message
        if rule is not UNSET:
            field_dict["rule"] = rule
        if severity is not UNSET:
            field_dict["severity"] = severity

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        signal = d.pop("signal")

        def _parse_baseline(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        baseline = _parse_baseline(d.pop("baseline", UNSET))

        def _parse_current(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        current = _parse_current(d.pop("current", UNSET))

        def _parse_delta(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        delta = _parse_delta(d.pop("delta", UNSET))

        def _parse_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        message = _parse_message(d.pop("message", UNSET))

        def _parse_rule(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rule = _parse_rule(d.pop("rule", UNSET))

        def _parse_severity(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        severity = _parse_severity(d.pop("severity", UNSET))

        drift_alert = cls(
            signal=signal,
            baseline=baseline,
            current=current,
            delta=delta,
            message=message,
            rule=rule,
            severity=severity,
        )

        drift_alert.additional_properties = d
        return drift_alert

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
