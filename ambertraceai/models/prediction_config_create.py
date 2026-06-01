from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prediction_config_create_backtest_config_type_0 import (
        PredictionConfigCreateBacktestConfigType0,
    )
    from ..models.prediction_config_create_eval_metric_config_type_0 import (
        PredictionConfigCreateEvalMetricConfigType0,
    )
    from ..models.prediction_config_create_feature_config_type_0 import (
        PredictionConfigCreateFeatureConfigType0,
    )


T = TypeVar("T", bound="PredictionConfigCreate")


@_attrs_define
class PredictionConfigCreate:
    """Create a prediction configuration for a platform.

    A prediction config defines **what** to predict (``target_field``),
    **how** to predict it (``model_type``, ``feature_fields``), and in
    which **mode** (``timeseries`` or ``cross_sectional``).

    **Choosing a mode:**

    - Use ``timeseries`` when your data has temporal ordering and you want
      to forecast future values (e.g. monthly bond yields, daily stock
      prices, quarterly revenue).  You must supply ``time_index_field``.
    - Use ``cross_sectional`` when each row is an independent observation
      and you want to predict a target from features (e.g. loan approval
      probability, fraud score, patient risk).  Omit ``time_index_field``.

        Attributes:
            target_field (str): Column name of the variable to predict. Must exist in the platform's dataset. Examples:
                'yield_10y', 'loan_approved', 'fraud_score'.
            backtest_config (None | PredictionConfigCreateBacktestConfigType0 | Unset): Backtesting configuration. Keys:
                'test_ratio' (float, default 0.2), 'n_splits' (int, default 1). In timeseries mode, uses expanding-window splits
                to prevent future leakage. In cross_sectional mode, uses stratified random splits.
            eval_metric (str | Unset): Primary evaluation metric. Options: 'rmse' (root mean squared error), 'mae' (mean
                absolute error), 'r2' (R-squared), 'dir_accuracy' (directional accuracy — timeseries only). Default: 'rmse'.
            eval_metric_config (None | PredictionConfigCreateEvalMetricConfigType0 | Unset): Additional metric
                configuration. Reserved for future use.
            feature_config (None | PredictionConfigCreateFeatureConfigType0 | Unset): Advanced feature engineering
                configuration (timeseries mode only). Controls which derived features are generated. Keys: 'lags' (list[int]),
                'rolling_mean' (list[int]), 'rolling_std' (list[int]), 'roc' (list[int] — rate of change), 'seasonal_dummies'
                (bool), 'differencing' (bool). Defaults are frequency-dependent. Ignored in cross_sectional mode.
            feature_fields (list[str] | None | Unset): Explicit list of column names to use as input features. If null, all
                numeric columns (excluding the target and time index) are used automatically. In cross_sectional mode, these are
                the raw columns fed directly to the model. In timeseries mode, these are the base columns from which lag/rolling
                features are derived.
            frequency (None | str | Unset): Temporal granularity of the data. One of: 'daily', 'weekly', 'monthly',
                'quarterly'. Determines default lag/rolling window sizes in timeseries mode. Omit for cross_sectional mode.
            horizon (int | None | Unset): Number of steps ahead to forecast. Only meaningful in timeseries mode — e.g.
                horizon=3 with frequency='monthly' predicts 3 months ahead. Omit or set to null for cross_sectional mode.
            mode (str | Unset): Prediction mode. 'timeseries' learns temporal patterns (lags, rolling windows, seasonality)
                and forecasts future values. 'cross_sectional' treats each row independently and learns a direct feature-to-
                target mapping. Default: 'timeseries'. Default: 'timeseries'.
            model_tier (str | Unset): Model complexity tier. Currently only 'tier1' (sklearn regressors) is supported.
                Default: 'tier1'.
            model_type (str | Unset): Algorithm to use. Options: 'gbt' (Gradient Boosted Trees — best general-purpose
                choice), 'ridge' (L2-regularised linear), 'lasso' (L1-regularised linear, good for sparse features). Default:
                'gbt'.
            time_index_field (None | str | Unset): Column containing date/time values used to order observations. Required
                for timeseries mode (e.g. 'date', 'observation_month'). Must be omitted or null for cross_sectional mode — rows
                have no temporal ordering.
    """

    target_field: str
    backtest_config: None | PredictionConfigCreateBacktestConfigType0 | Unset = UNSET
    eval_metric: str | Unset = "rmse"
    eval_metric_config: None | PredictionConfigCreateEvalMetricConfigType0 | Unset = (
        UNSET
    )
    feature_config: None | PredictionConfigCreateFeatureConfigType0 | Unset = UNSET
    feature_fields: list[str] | None | Unset = UNSET
    frequency: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    mode: str | Unset = "timeseries"
    model_tier: str | Unset = "tier1"
    model_type: str | Unset = "gbt"
    time_index_field: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_config_create_backtest_config_type_0 import (
            PredictionConfigCreateBacktestConfigType0,
        )
        from ..models.prediction_config_create_eval_metric_config_type_0 import (
            PredictionConfigCreateEvalMetricConfigType0,
        )
        from ..models.prediction_config_create_feature_config_type_0 import (
            PredictionConfigCreateFeatureConfigType0,
        )

        target_field = self.target_field

        backtest_config: dict[str, Any] | None | Unset
        if isinstance(self.backtest_config, Unset):
            backtest_config = UNSET
        elif isinstance(
            self.backtest_config, PredictionConfigCreateBacktestConfigType0
        ):
            backtest_config = self.backtest_config.to_dict()
        else:
            backtest_config = self.backtest_config

        eval_metric = self.eval_metric

        eval_metric_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_metric_config, Unset):
            eval_metric_config = UNSET
        elif isinstance(
            self.eval_metric_config, PredictionConfigCreateEvalMetricConfigType0
        ):
            eval_metric_config = self.eval_metric_config.to_dict()
        else:
            eval_metric_config = self.eval_metric_config

        feature_config: dict[str, Any] | None | Unset
        if isinstance(self.feature_config, Unset):
            feature_config = UNSET
        elif isinstance(self.feature_config, PredictionConfigCreateFeatureConfigType0):
            feature_config = self.feature_config.to_dict()
        else:
            feature_config = self.feature_config

        feature_fields: list[str] | None | Unset
        if isinstance(self.feature_fields, Unset):
            feature_fields = UNSET
        elif isinstance(self.feature_fields, list):
            feature_fields = self.feature_fields

        else:
            feature_fields = self.feature_fields

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

        model_tier = self.model_tier

        model_type = self.model_type

        time_index_field: None | str | Unset
        if isinstance(self.time_index_field, Unset):
            time_index_field = UNSET
        else:
            time_index_field = self.time_index_field

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target_field": target_field,
            }
        )
        if backtest_config is not UNSET:
            field_dict["backtest_config"] = backtest_config
        if eval_metric is not UNSET:
            field_dict["eval_metric"] = eval_metric
        if eval_metric_config is not UNSET:
            field_dict["eval_metric_config"] = eval_metric_config
        if feature_config is not UNSET:
            field_dict["feature_config"] = feature_config
        if feature_fields is not UNSET:
            field_dict["feature_fields"] = feature_fields
        if frequency is not UNSET:
            field_dict["frequency"] = frequency
        if horizon is not UNSET:
            field_dict["horizon"] = horizon
        if mode is not UNSET:
            field_dict["mode"] = mode
        if model_tier is not UNSET:
            field_dict["model_tier"] = model_tier
        if model_type is not UNSET:
            field_dict["model_type"] = model_type
        if time_index_field is not UNSET:
            field_dict["time_index_field"] = time_index_field

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prediction_config_create_backtest_config_type_0 import (
            PredictionConfigCreateBacktestConfigType0,
        )
        from ..models.prediction_config_create_eval_metric_config_type_0 import (
            PredictionConfigCreateEvalMetricConfigType0,
        )
        from ..models.prediction_config_create_feature_config_type_0 import (
            PredictionConfigCreateFeatureConfigType0,
        )

        d = dict(src_dict)
        target_field = d.pop("target_field")

        def _parse_backtest_config(
            data: object,
        ) -> None | PredictionConfigCreateBacktestConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backtest_config_type_0 = (
                    PredictionConfigCreateBacktestConfigType0.from_dict(data)
                )

                return backtest_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigCreateBacktestConfigType0 | Unset, data)

        backtest_config = _parse_backtest_config(d.pop("backtest_config", UNSET))

        eval_metric = d.pop("eval_metric", UNSET)

        def _parse_eval_metric_config(
            data: object,
        ) -> None | PredictionConfigCreateEvalMetricConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_metric_config_type_0 = (
                    PredictionConfigCreateEvalMetricConfigType0.from_dict(data)
                )

                return eval_metric_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PredictionConfigCreateEvalMetricConfigType0 | Unset, data
            )

        eval_metric_config = _parse_eval_metric_config(
            d.pop("eval_metric_config", UNSET)
        )

        def _parse_feature_config(
            data: object,
        ) -> None | PredictionConfigCreateFeatureConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_config_type_0 = (
                    PredictionConfigCreateFeatureConfigType0.from_dict(data)
                )

                return feature_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigCreateFeatureConfigType0 | Unset, data)

        feature_config = _parse_feature_config(d.pop("feature_config", UNSET))

        def _parse_feature_fields(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                feature_fields_type_0 = cast(list[str], data)

                return feature_fields_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        feature_fields = _parse_feature_fields(d.pop("feature_fields", UNSET))

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

        model_tier = d.pop("model_tier", UNSET)

        model_type = d.pop("model_type", UNSET)

        def _parse_time_index_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time_index_field = _parse_time_index_field(d.pop("time_index_field", UNSET))

        prediction_config_create = cls(
            target_field=target_field,
            backtest_config=backtest_config,
            eval_metric=eval_metric,
            eval_metric_config=eval_metric_config,
            feature_config=feature_config,
            feature_fields=feature_fields,
            frequency=frequency,
            horizon=horizon,
            mode=mode,
            model_tier=model_tier,
            model_type=model_type,
            time_index_field=time_index_field,
        )

        prediction_config_create.additional_properties = d
        return prediction_config_create

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
