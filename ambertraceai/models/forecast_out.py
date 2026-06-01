from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.forecast_out_features_used_type_0 import ForecastOutFeaturesUsedType0
    from ..models.forecast_out_rule_adjustments_type_0 import (
        ForecastOutRuleAdjustmentsType0,
    )


T = TypeVar("T", bound="ForecastOut")


@_attrs_define
class ForecastOut:
    """A single forecast record from prediction history.

    Attributes:
        id (int):
        prediction_model_id (int):
        value (float): Point prediction value.
        actual_value (float | None | Unset): Actual observed value, backfilled when available for accuracy tracking.
        created_at (None | str | Unset):
        features_used (ForecastOutFeaturesUsedType0 | None | Unset): Feature values used to generate this prediction.
        forecast_date (None | str | Unset): ISO 8601 date of the forecast (timeseries) or creation time
            (cross_sectional).
        horizon (int | None | Unset): Forecast horizon (timeseries only).
        lower_bound (float | None | Unset): Lower bound of the prediction interval.
        rule_adjustments (ForecastOutRuleAdjustmentsType0 | None | Unset): Audit trail of symbolic rules that fired and
            their effects.
        upper_bound (float | None | Unset): Upper bound of the prediction interval.
    """

    id: int
    prediction_model_id: int
    value: float
    actual_value: float | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    features_used: ForecastOutFeaturesUsedType0 | None | Unset = UNSET
    forecast_date: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    lower_bound: float | None | Unset = UNSET
    rule_adjustments: ForecastOutRuleAdjustmentsType0 | None | Unset = UNSET
    upper_bound: float | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.forecast_out_features_used_type_0 import (
            ForecastOutFeaturesUsedType0,
        )
        from ..models.forecast_out_rule_adjustments_type_0 import (
            ForecastOutRuleAdjustmentsType0,
        )

        id = self.id

        prediction_model_id = self.prediction_model_id

        value = self.value

        actual_value: float | None | Unset
        if isinstance(self.actual_value, Unset):
            actual_value = UNSET
        else:
            actual_value = self.actual_value

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        features_used: dict[str, Any] | None | Unset
        if isinstance(self.features_used, Unset):
            features_used = UNSET
        elif isinstance(self.features_used, ForecastOutFeaturesUsedType0):
            features_used = self.features_used.to_dict()
        else:
            features_used = self.features_used

        forecast_date: None | str | Unset
        if isinstance(self.forecast_date, Unset):
            forecast_date = UNSET
        else:
            forecast_date = self.forecast_date

        horizon: int | None | Unset
        if isinstance(self.horizon, Unset):
            horizon = UNSET
        else:
            horizon = self.horizon

        lower_bound: float | None | Unset
        if isinstance(self.lower_bound, Unset):
            lower_bound = UNSET
        else:
            lower_bound = self.lower_bound

        rule_adjustments: dict[str, Any] | None | Unset
        if isinstance(self.rule_adjustments, Unset):
            rule_adjustments = UNSET
        elif isinstance(self.rule_adjustments, ForecastOutRuleAdjustmentsType0):
            rule_adjustments = self.rule_adjustments.to_dict()
        else:
            rule_adjustments = self.rule_adjustments

        upper_bound: float | None | Unset
        if isinstance(self.upper_bound, Unset):
            upper_bound = UNSET
        else:
            upper_bound = self.upper_bound

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "prediction_model_id": prediction_model_id,
                "value": value,
            }
        )
        if actual_value is not UNSET:
            field_dict["actual_value"] = actual_value
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if features_used is not UNSET:
            field_dict["features_used"] = features_used
        if forecast_date is not UNSET:
            field_dict["forecast_date"] = forecast_date
        if horizon is not UNSET:
            field_dict["horizon"] = horizon
        if lower_bound is not UNSET:
            field_dict["lower_bound"] = lower_bound
        if rule_adjustments is not UNSET:
            field_dict["rule_adjustments"] = rule_adjustments
        if upper_bound is not UNSET:
            field_dict["upper_bound"] = upper_bound

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.forecast_out_features_used_type_0 import (
            ForecastOutFeaturesUsedType0,
        )
        from ..models.forecast_out_rule_adjustments_type_0 import (
            ForecastOutRuleAdjustmentsType0,
        )

        d = dict(src_dict)
        id = d.pop("id")

        prediction_model_id = d.pop("prediction_model_id")

        value = d.pop("value")

        def _parse_actual_value(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        actual_value = _parse_actual_value(d.pop("actual_value", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_features_used(
            data: object,
        ) -> ForecastOutFeaturesUsedType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                features_used_type_0 = ForecastOutFeaturesUsedType0.from_dict(data)

                return features_used_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ForecastOutFeaturesUsedType0 | None | Unset, data)

        features_used = _parse_features_used(d.pop("features_used", UNSET))

        def _parse_forecast_date(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        forecast_date = _parse_forecast_date(d.pop("forecast_date", UNSET))

        def _parse_horizon(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        horizon = _parse_horizon(d.pop("horizon", UNSET))

        def _parse_lower_bound(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        lower_bound = _parse_lower_bound(d.pop("lower_bound", UNSET))

        def _parse_rule_adjustments(
            data: object,
        ) -> ForecastOutRuleAdjustmentsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                rule_adjustments_type_0 = ForecastOutRuleAdjustmentsType0.from_dict(
                    data
                )

                return rule_adjustments_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ForecastOutRuleAdjustmentsType0 | None | Unset, data)

        rule_adjustments = _parse_rule_adjustments(d.pop("rule_adjustments", UNSET))

        def _parse_upper_bound(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        upper_bound = _parse_upper_bound(d.pop("upper_bound", UNSET))

        forecast_out = cls(
            id=id,
            prediction_model_id=prediction_model_id,
            value=value,
            actual_value=actual_value,
            created_at=created_at,
            features_used=features_used,
            forecast_date=forecast_date,
            horizon=horizon,
            lower_bound=lower_bound,
            rule_adjustments=rule_adjustments,
            upper_bound=upper_bound,
        )

        forecast_out.additional_properties = d
        return forecast_out

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
