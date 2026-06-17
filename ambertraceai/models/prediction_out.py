from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prediction_out_explanation_type_0 import PredictionOutExplanationType0
    from ..models.prediction_out_prediction import PredictionOutPrediction


T = TypeVar("T", bound="PredictionOut")


@_attrs_define
class PredictionOut:
    """Prediction result returned by the predict endpoint.

    Attributes:
        platform_id (int):
        prediction (PredictionOutPrediction): Prediction result containing 'value' (point prediction), 'lower_bound',
            'upper_bound' (confidence interval), and 'raw_value' (before rule adjustments).
        target (str): Name of the predicted target field.
        explanation (None | PredictionOutExplanationType0 | Unset): Detailed explanation when explain=true. Contains
            'feature_importance' (sorted list), 'adjustment_rules_fired', 'constraint_rules_fired', 'model' metadata, and
            optionally 'narrative' (LLM-generated summary).
        frequency (None | str | Unset):
        horizon (int | None | Unset): Forecast horizon (steps ahead). Null for cross_sectional.
        mode (str | Unset): Prediction mode used: 'timeseries' or 'cross_sectional'. Default: 'timeseries'.
        unmatched_overrides (list[str] | None | Unset): Override keys from feature_overrides that mapped to NO feature
            the trained model consumes and were therefore ignored. Present only when at least one override could not be
            applied — for timeseries, a raw column with no engineered feature in the model; for cross_sectional, a key
            matching no model feature. Omitted (null) when every override was applied.
    """

    platform_id: int
    prediction: PredictionOutPrediction
    target: str
    explanation: None | PredictionOutExplanationType0 | Unset = UNSET
    frequency: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    mode: str | Unset = "timeseries"
    unmatched_overrides: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_out_explanation_type_0 import (
            PredictionOutExplanationType0,
        )

        platform_id = self.platform_id

        prediction = self.prediction.to_dict()

        target = self.target

        explanation: dict[str, Any] | None | Unset
        if isinstance(self.explanation, Unset):
            explanation = UNSET
        elif isinstance(self.explanation, PredictionOutExplanationType0):
            explanation = self.explanation.to_dict()
        else:
            explanation = self.explanation

        frequency: None | str | Unset
        if isinstance(self.frequency, Unset):
            frequency = UNSET
        else:
            frequency = self.frequency

        horizon: int | None | Unset
        if isinstance(self.horizon, Unset):
            horizon = UNSET
        else:
            horizon = self.horizon

        mode = self.mode

        unmatched_overrides: list[str] | None | Unset
        if isinstance(self.unmatched_overrides, Unset):
            unmatched_overrides = UNSET
        elif isinstance(self.unmatched_overrides, list):
            unmatched_overrides = self.unmatched_overrides

        else:
            unmatched_overrides = self.unmatched_overrides

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_id": platform_id,
                "prediction": prediction,
                "target": target,
            }
        )
        if explanation is not UNSET:
            field_dict["explanation"] = explanation
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if horizon is not UNSET:
            field_dict["horizon"] = horizon
        if mode is not UNSET:
            field_dict["mode"] = mode
        if unmatched_overrides is not UNSET:
            field_dict["unmatched_overrides"] = unmatched_overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prediction_out_explanation_type_0 import (
            PredictionOutExplanationType0,
        )
        from ..models.prediction_out_prediction import PredictionOutPrediction

        d = dict(src_dict)
        platform_id = d.pop("platform_id")

        prediction = PredictionOutPrediction.from_dict(d.pop("prediction"))

        target = d.pop("target")

        def _parse_explanation(
            data: object,
        ) -> None | PredictionOutExplanationType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                explanation_type_0 = PredictionOutExplanationType0.from_dict(data)

                return explanation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionOutExplanationType0 | Unset, data)

        explanation = _parse_explanation(d.pop("explanation", UNSET))

        def _parse_frequency(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        frequency = _parse_frequency(d.pop("frequency", UNSET))

        def _parse_horizon(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        horizon = _parse_horizon(d.pop("horizon", UNSET))

        mode = d.pop("mode", UNSET)

        def _parse_unmatched_overrides(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                unmatched_overrides_type_0 = cast(list[str], data)

                return unmatched_overrides_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        unmatched_overrides = _parse_unmatched_overrides(
            d.pop("unmatched_overrides", UNSET)
        )

        prediction_out = cls(
            platform_id=platform_id,
            prediction=prediction,
            target=target,
            explanation=explanation,
            frequency=frequency,
            horizon=horizon,
            mode=mode,
            unmatched_overrides=unmatched_overrides,
        )

        prediction_out.additional_properties = d
        return prediction_out

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
