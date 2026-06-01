from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.eval_config_update_calculation_type_0 import (
        EvalConfigUpdateCalculationType0,
    )


T = TypeVar("T", bound="EvalConfigUpdate")


@_attrs_define
class EvalConfigUpdate:
    """
    Attributes:
        direction (str):
        target_metric (str):
        calculation (EvalConfigUpdateCalculationType0 | None | Unset):
        description (str | Unset):  Default: ''.
        min_positive_fraction (float | None | Unset):
        significance_threshold_pp (float | None | Unset):
        unit (str | Unset):  Default: 'other'.
    """

    direction: str
    target_metric: str
    calculation: EvalConfigUpdateCalculationType0 | None | Unset = UNSET
    description: str | Unset = ""
    min_positive_fraction: float | None | Unset = UNSET
    significance_threshold_pp: float | None | Unset = UNSET
    unit: str | Unset = "other"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.eval_config_update_calculation_type_0 import (
            EvalConfigUpdateCalculationType0,
        )

        direction = self.direction

        target_metric = self.target_metric

        calculation: dict[str, Any] | None | Unset
        if isinstance(self.calculation, Unset):
            calculation = UNSET
        elif isinstance(self.calculation, EvalConfigUpdateCalculationType0):
            calculation = self.calculation.to_dict()
        else:
            calculation = self.calculation

        description = self.description

        min_positive_fraction: float | None | Unset
        if isinstance(self.min_positive_fraction, Unset):
            min_positive_fraction = UNSET
        else:
            min_positive_fraction = self.min_positive_fraction

        significance_threshold_pp: float | None | Unset
        if isinstance(self.significance_threshold_pp, Unset):
            significance_threshold_pp = UNSET
        else:
            significance_threshold_pp = self.significance_threshold_pp

        unit = self.unit

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "direction": direction,
                "target_metric": target_metric,
            }
        )
        if calculation is not UNSET:
            field_dict["calculation"] = calculation
        if description is not UNSET:
            field_dict["description"] = description
        if min_positive_fraction is not UNSET:
            field_dict["min_positive_fraction"] = min_positive_fraction
        if significance_threshold_pp is not UNSET:
            field_dict["significance_threshold_pp"] = significance_threshold_pp
        if unit is not UNSET:
            field_dict["unit"] = unit

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.eval_config_update_calculation_type_0 import (
            EvalConfigUpdateCalculationType0,
        )

        d = dict(src_dict)
        direction = d.pop("direction")

        target_metric = d.pop("target_metric")

        def _parse_calculation(
            data: object,
        ) -> EvalConfigUpdateCalculationType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                calculation_type_0 = EvalConfigUpdateCalculationType0.from_dict(data)

                return calculation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(EvalConfigUpdateCalculationType0 | None | Unset, data)

        calculation = _parse_calculation(d.pop("calculation", UNSET))

        description = d.pop("description", UNSET)

        def _parse_min_positive_fraction(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_positive_fraction = _parse_min_positive_fraction(
            d.pop("min_positive_fraction", UNSET)
        )

        def _parse_significance_threshold_pp(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        significance_threshold_pp = _parse_significance_threshold_pp(
            d.pop("significance_threshold_pp", UNSET)
        )

        unit = d.pop("unit", UNSET)

        eval_config_update = cls(
            direction=direction,
            target_metric=target_metric,
            calculation=calculation,
            description=description,
            min_positive_fraction=min_positive_fraction,
            significance_threshold_pp=significance_threshold_pp,
            unit=unit,
        )

        eval_config_update.additional_properties = d
        return eval_config_update

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
