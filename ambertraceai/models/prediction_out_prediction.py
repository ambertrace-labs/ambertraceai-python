from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="PredictionOutPrediction")


@_attrs_define
class PredictionOutPrediction:
    """Prediction result. Since 1.0.0 'value' is the LEVEL by default: for a differenced target it is the reconstructed
    level (baseline + change), NOT the raw month-over-month change. The change is exposed alongside as 'value_change'
    (null for a non-differenced target; for the reconstructable path value == baseline + value_change). Also
    'lower_bound'/'upper_bound' (confidence interval). Value-space labelling so the consumer knows which space 'value'
    is in without a second call: 'value_space' ('level' — the point is a level, i.e. no transform or a difference
    reconstructed back to the level; or 'transformed_unreconstructed' — a raw CHANGE that could not be reconstructed to
    a level because a difference transform had no base history, treat 'value' as unreliable), 'target_transform' (the
    EFFECTIVE, post-'auto'-resolution transform applied at train time), and 'baseline' (the level used to reconstruct a
    differenced forecast, or null when not applicable).

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        prediction_out_prediction = cls()

        prediction_out_prediction.additional_properties = d
        return prediction_out_prediction

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
