from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prediction_config_out_backtest_config_type_0 import (
        PredictionConfigOutBacktestConfigType0,
    )
    from ..models.prediction_config_out_eval_metric_config_type_0 import (
        PredictionConfigOutEvalMetricConfigType0,
    )
    from ..models.prediction_config_out_feature_config_type_0 import (
        PredictionConfigOutFeatureConfigType0,
    )


T = TypeVar("T", bound="PredictionConfigOut")


@_attrs_define
class PredictionConfigOut:
    """Prediction configuration as returned by the API.

    Attributes:
        eval_metric (str):
        id (int):
        model_tier (str):
        model_type (str):
        organisation_id (str):
        platform_id (int):
        status (str): Config lifecycle status: 'pending' (created, not yet trained), 'training' (training in progress),
            'trained' (ready to predict), 'failed' (training failed — see error_message).
        target_field (str):
        autoregressive (str | Unset): Autoregression control: 'full' (history allowed, default), 'limited' (drivers + a
            little history), or 'none' (drivers only). Default: 'full'.
        backtest_config (None | PredictionConfigOutBacktestConfigType0 | Unset):
        created_at (None | str | Unset):
        error_message (None | str | Unset): Human-readable error details when status is 'failed'.
        eval_metric_config (None | PredictionConfigOutEvalMetricConfigType0 | Unset):
        feature_config (None | PredictionConfigOutFeatureConfigType0 | Unset):
        feature_fields (list[str] | None | Unset):
        frequency (None | str | Unset):
        horizon (int | None | Unset):
        max_ar_lag (int | None | Unset): Advanced numeric autoregression cap (overrides the enum when set): 0 = drivers
            only, k = target-history features with lag/window <= k.
        mode (str | Unset): Prediction mode: 'timeseries' or 'cross_sectional'. Default: 'timeseries'.
        output_space (None | str | Unset): Item 6 — the space predict() 'value' will be in given the resolved transform:
            'level' (transform 'none' — value is a level) or 'change' (a differencing transform — predict() reconstructs to
            a level when history is available; see the predict response's 'value_space'). 'unknown (auto — resolved at train
            time)' before an 'auto' config is trained. Null for cross_sectional configs.
        resolved_target_transform (None | str | Unset): Item 6 — the EFFECTIVE target transform, echoed on the config so
            the output space is known without predicting. When a concrete transform was requested ('none' or 'difference')
            this echoes it immediately at create_config time. When 'auto' was requested it resolves at TRAIN time, so before
            training this reads 'auto (resolved at train time)'; once trained it reflects the concrete transform the trainer
            chose (persisted back onto the config). Null for cross_sectional configs.
        target_transform_reason (None | str | Unset): Why the resolved transform was chosen (the auto-heuristic detail,
            or 'explicit'). Populated once trained (or when the config carries it). Null otherwise.
        time_index_field (None | str | Unset):
        updated_at (None | str | Unset):
    """

    eval_metric: str
    id: int
    model_tier: str
    model_type: str
    organisation_id: str
    platform_id: int
    status: str
    target_field: str
    autoregressive: str | Unset = "full"
    backtest_config: None | PredictionConfigOutBacktestConfigType0 | Unset = UNSET
    created_at: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    eval_metric_config: None | PredictionConfigOutEvalMetricConfigType0 | Unset = UNSET
    feature_config: None | PredictionConfigOutFeatureConfigType0 | Unset = UNSET
    feature_fields: list[str] | None | Unset = UNSET
    frequency: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    max_ar_lag: int | None | Unset = UNSET
    mode: str | Unset = "timeseries"
    output_space: None | str | Unset = UNSET
    resolved_target_transform: None | str | Unset = UNSET
    target_transform_reason: None | str | Unset = UNSET
    time_index_field: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_config_out_backtest_config_type_0 import (
            PredictionConfigOutBacktestConfigType0,
        )
        from ..models.prediction_config_out_eval_metric_config_type_0 import (
            PredictionConfigOutEvalMetricConfigType0,
        )
        from ..models.prediction_config_out_feature_config_type_0 import (
            PredictionConfigOutFeatureConfigType0,
        )

        eval_metric = self.eval_metric

        id = self.id

        model_tier = self.model_tier

        model_type = self.model_type

        organisation_id = self.organisation_id

        platform_id = self.platform_id

        status = self.status

        target_field = self.target_field

        autoregressive = self.autoregressive

        backtest_config: dict[str, Any] | None | Unset
        if isinstance(self.backtest_config, Unset):
            backtest_config = UNSET
        elif isinstance(self.backtest_config, PredictionConfigOutBacktestConfigType0):
            backtest_config = self.backtest_config.to_dict()
        else:
            backtest_config = self.backtest_config

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        eval_metric_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_metric_config, Unset):
            eval_metric_config = UNSET
        elif isinstance(
            self.eval_metric_config, PredictionConfigOutEvalMetricConfigType0
        ):
            eval_metric_config = self.eval_metric_config.to_dict()
        else:
            eval_metric_config = self.eval_metric_config

        feature_config: dict[str, Any] | None | Unset
        if isinstance(self.feature_config, Unset):
            feature_config = UNSET
        elif isinstance(self.feature_config, PredictionConfigOutFeatureConfigType0):
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

        max_ar_lag: int | None | Unset
        if isinstance(self.max_ar_lag, Unset):
            max_ar_lag = UNSET
        else:
            max_ar_lag = self.max_ar_lag

        mode = self.mode

        output_space: None | str | Unset
        if isinstance(self.output_space, Unset):
            output_space = UNSET
        else:
            output_space = self.output_space

        resolved_target_transform: None | str | Unset
        if isinstance(self.resolved_target_transform, Unset):
            resolved_target_transform = UNSET
        else:
            resolved_target_transform = self.resolved_target_transform

        target_transform_reason: None | str | Unset
        if isinstance(self.target_transform_reason, Unset):
            target_transform_reason = UNSET
        else:
            target_transform_reason = self.target_transform_reason

        time_index_field: None | str | Unset
        if isinstance(self.time_index_field, Unset):
            time_index_field = UNSET
        else:
            time_index_field = self.time_index_field

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "eval_metric": eval_metric,
                "id": id,
                "model_tier": model_tier,
                "model_type": model_type,
                "organisation_id": organisation_id,
                "platform_id": platform_id,
                "status": status,
                "target_field": target_field,
            }
        )
        if autoregressive is not UNSET:
            field_dict["autoregressive"] = autoregressive
        if backtest_config is not UNSET:
            field_dict["backtest_config"] = backtest_config
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
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
        if max_ar_lag is not UNSET:
            field_dict["max_ar_lag"] = max_ar_lag
        if mode is not UNSET:
            field_dict["mode"] = mode
        if output_space is not UNSET:
            field_dict["output_space"] = output_space
        if resolved_target_transform is not UNSET:
            field_dict["resolved_target_transform"] = resolved_target_transform
        if target_transform_reason is not UNSET:
            field_dict["target_transform_reason"] = target_transform_reason
        if time_index_field is not UNSET:
            field_dict["time_index_field"] = time_index_field
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prediction_config_out_backtest_config_type_0 import (
            PredictionConfigOutBacktestConfigType0,
        )
        from ..models.prediction_config_out_eval_metric_config_type_0 import (
            PredictionConfigOutEvalMetricConfigType0,
        )
        from ..models.prediction_config_out_feature_config_type_0 import (
            PredictionConfigOutFeatureConfigType0,
        )

        d = dict(src_dict)
        eval_metric = d.pop("eval_metric")

        id = d.pop("id")

        model_tier = d.pop("model_tier")

        model_type = d.pop("model_type")

        organisation_id = d.pop("organisation_id")

        platform_id = d.pop("platform_id")

        status = d.pop("status")

        target_field = d.pop("target_field")

        autoregressive = d.pop("autoregressive", UNSET)

        def _parse_backtest_config(
            data: object,
        ) -> None | PredictionConfigOutBacktestConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backtest_config_type_0 = (
                    PredictionConfigOutBacktestConfigType0.from_dict(data)
                )

                return backtest_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutBacktestConfigType0 | Unset, data)

        backtest_config = _parse_backtest_config(d.pop("backtest_config", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_eval_metric_config(
            data: object,
        ) -> None | PredictionConfigOutEvalMetricConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_metric_config_type_0 = (
                    PredictionConfigOutEvalMetricConfigType0.from_dict(data)
                )

                return eval_metric_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutEvalMetricConfigType0 | Unset, data)

        eval_metric_config = _parse_eval_metric_config(
            d.pop("eval_metric_config", UNSET)
        )

        def _parse_feature_config(
            data: object,
        ) -> None | PredictionConfigOutFeatureConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_config_type_0 = PredictionConfigOutFeatureConfigType0.from_dict(
                    data
                )

                return feature_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutFeatureConfigType0 | Unset, data)

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

        def _parse_max_ar_lag(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_ar_lag = _parse_max_ar_lag(d.pop("max_ar_lag", UNSET))

        mode = d.pop("mode", UNSET)

        def _parse_output_space(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_space = _parse_output_space(d.pop("output_space", UNSET))

        def _parse_resolved_target_transform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolved_target_transform = _parse_resolved_target_transform(
            d.pop("resolved_target_transform", UNSET)
        )

        def _parse_target_transform_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        target_transform_reason = _parse_target_transform_reason(
            d.pop("target_transform_reason", UNSET)
        )

        def _parse_time_index_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time_index_field = _parse_time_index_field(d.pop("time_index_field", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        prediction_config_out = cls(
            eval_metric=eval_metric,
            id=id,
            model_tier=model_tier,
            model_type=model_type,
            organisation_id=organisation_id,
            platform_id=platform_id,
            status=status,
            target_field=target_field,
            autoregressive=autoregressive,
            backtest_config=backtest_config,
            created_at=created_at,
            error_message=error_message,
            eval_metric_config=eval_metric_config,
            feature_config=feature_config,
            feature_fields=feature_fields,
            frequency=frequency,
            horizon=horizon,
            max_ar_lag=max_ar_lag,
            mode=mode,
            output_space=output_space,
            resolved_target_transform=resolved_target_transform,
            target_transform_reason=target_transform_reason,
            time_index_field=time_index_field,
            updated_at=updated_at,
        )

        prediction_config_out.additional_properties = d
        return prediction_config_out

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
