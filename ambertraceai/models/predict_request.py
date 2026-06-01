from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.predict_request_feature_overrides_type_0 import (
        PredictRequestFeatureOverridesType0,
    )


T = TypeVar("T", bound="PredictRequest")


@_attrs_define
class PredictRequest:
    """Request body for running a prediction.

    **How feature_overrides work by mode:**

    - **timeseries**: Overrides propagate through lag features. For example,
      ``{"inflation": 5.0}`` sets the latest inflation value, which then
      affects ``inflation_lag_1``, ``inflation_rolling_mean_3``, etc.
      Useful for what-if analysis ("what if inflation hits 5%?").

    - **cross_sectional**: Overrides ARE the input row. Each key-value pair
      maps directly to a model feature. For example,
      ``{"credit_score": 720, "debt_to_income": 0.35}`` provides the exact
      feature values for prediction. You should supply all feature_fields
      defined in the config for best results.

        Attributes:
            prediction_config_id (int): ID of a trained prediction config on this platform.
            explain (bool | Unset): Whether to include a detailed explanation in the response: feature importance, fired
                rules, model metadata, and an optional LLM-generated narrative. Default: True.
            feature_overrides (None | PredictRequestFeatureOverridesType0 | Unset): Map of raw column names to override
                values. In cross_sectional mode, these define the input observation (supply all features for best results). In
                timeseries mode, these override the latest known values before lag/rolling feature derivation. Keys must match
                column names in the dataset.
    """

    prediction_config_id: int
    explain: bool | Unset = True
    feature_overrides: None | PredictRequestFeatureOverridesType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.predict_request_feature_overrides_type_0 import (
            PredictRequestFeatureOverridesType0,
        )

        prediction_config_id = self.prediction_config_id

        explain = self.explain

        feature_overrides: dict[str, Any] | None | Unset
        if isinstance(self.feature_overrides, Unset):
            feature_overrides = UNSET
        elif isinstance(self.feature_overrides, PredictRequestFeatureOverridesType0):
            feature_overrides = self.feature_overrides.to_dict()
        else:
            feature_overrides = self.feature_overrides

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prediction_config_id": prediction_config_id,
            }
        )
        if explain is not UNSET:
            field_dict["explain"] = explain
        if feature_overrides is not UNSET:
            field_dict["feature_overrides"] = feature_overrides

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.predict_request_feature_overrides_type_0 import (
            PredictRequestFeatureOverridesType0,
        )

        d = dict(src_dict)
        prediction_config_id = d.pop("prediction_config_id")

        explain = d.pop("explain", UNSET)

        def _parse_feature_overrides(
            data: object,
        ) -> None | PredictRequestFeatureOverridesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_overrides_type_0 = (
                    PredictRequestFeatureOverridesType0.from_dict(data)
                )

                return feature_overrides_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictRequestFeatureOverridesType0 | Unset, data)

        feature_overrides = _parse_feature_overrides(d.pop("feature_overrides", UNSET))

        predict_request = cls(
            prediction_config_id=prediction_config_id,
            explain=explain,
            feature_overrides=feature_overrides,
        )

        predict_request.additional_properties = d
        return predict_request

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
