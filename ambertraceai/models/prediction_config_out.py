from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.prediction_config_out_objective import PredictionConfigOutObjective
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prediction_config_out_backtest_config_type_0 import PredictionConfigOutBacktestConfigType0
    from ..models.prediction_config_out_eval_metric_config_type_0 import PredictionConfigOutEvalMetricConfigType0
    from ..models.prediction_config_out_feature_config_type_0 import PredictionConfigOutFeatureConfigType0
    from ..models.prediction_config_out_panel_sufficiency_type_0 import PredictionConfigOutPanelSufficiencyType0
    from ..models.prediction_config_out_reduction_manifest_type_0 import PredictionConfigOutReductionManifestType0


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
        auto_reduce (bool | Unset): Whether auto-reduce is opted in — drop the sparsest auxiliary columns to meet a
            declared sufficiency bar instead of returning HTTP 409. Default: False.
        autoregressive (str | Unset): Autoregression control: 'full' (history allowed, default), 'limited' (drivers + a
            little history), or 'none' (drivers only). Default: 'full'.
        backtest_config (None | PredictionConfigOutBacktestConfigType0 | Unset):
        baseline_mode (str | Unset): Forecast anchor mode: 'neural' (default), 'persistence', or 'drift'. Default:
            'neural'.
        core_columns (list[str] | None | Unset): Declared never-drop columns. The target_field and time_index_field are
            implicitly core regardless of this list.
        created_at (None | str | Unset):
        discovery_mode (bool | Unset): Whether this config runs in discovery mode: True when feature_fields is null (the
            platform auto-discovers ALL numeric columns as candidate drivers), False when an explicit feature set is
            supplied. Discovery is the mainline usage — target + features, no recipe. Default: False.
        error_message (None | str | Unset): Human-readable error details when status is 'failed'.
        eval_metric_config (None | PredictionConfigOutEvalMetricConfigType0 | Unset):
        feature_config (None | PredictionConfigOutFeatureConfigType0 | Unset):
        feature_fields (list[str] | None | Unset):
        frequency (None | str | Unset):
        horizon (int | None | Unset):
        max_ar_lag (int | None | Unset): Advanced numeric autoregression cap (overrides the enum when set): 0 = drivers
            only, k = target-history features with lag/window <= k.
        min_history_years (float | None | Unset): Declared minimum history span (years) for the sufficiency gate.
        min_rows (int | None | Unset): Declared minimum post-warmup row count for the sufficiency gate.
        mode (str | Unset): Prediction mode: 'timeseries' or 'cross_sectional'. Default: 'timeseries'.
        neural_confidence_tau (float | Unset): Per-point neural-tier confidence threshold: GBT prediction admitted as
            neural_scored when confidence >= tau, else neural_weak (raw GBT still served). 0.0 = gate labels only. Default:
            0.0.
        objective (PredictionConfigOutObjective | Unset): Optimisation objective selection. The metric is computed and
            reported; the configured objective currently does not drive rule acceptance. Default:
            PredictionConfigOutObjective.SKILL_VS_PERSISTENCE.
        output_space (None | str | Unset): Item 6 — the space predict() 'value' will be in given the resolved transform:
            'level' (transform 'none' — value is a level) or 'change' (a differencing transform — predict() reconstructs to
            a level when history is available; see the predict response's 'value_space'). 'unknown (auto — resolved at train
            time)' before an 'auto' config is trained, and for a stored out-of-set transform (the engine falls back to
            auto). Null for cross_sectional configs.
        panel_sufficiency (None | PredictionConfigOutPanelSufficiencyType0 | Unset): Panel sufficiency advisory from the
            dataset's schema_info. Contains tradeoff_curve, recovery_groups, and summary metrics when the dataset has been
            analysed for missing-value patterns. Null when unavailable.
        reduction_manifest (None | PredictionConfigOutReductionManifestType0 | Unset): Manifest from the most recent
            auto_reduce run: 'dropped_columns' (per-column {column, action:'dropped_auxiliary', null_count}),
            'usable_rows_before'/'usable_rows_after', 'target_rows', 'target_years', 'usable_span_years_after'. Null when
            auto_reduce has never run or the panel already met the declared bar.
        regime_platform_id (int | None | Unset): ID of the Decisions platform used for regime conditioning Null when no
            regime platform is configured.
        resolved_target_transform (None | str | Unset): Item 6 — the EFFECTIVE target transform, echoed on the config so
            the output space is known without predicting. When a concrete transform was requested ('none' or 'difference')
            this echoes it immediately at create_config time. When 'auto' was requested it resolves at TRAIN time, so before
            training this reads 'auto (resolved at train time)'; once trained it reflects the concrete transform the trainer
            chose (persisted back onto the config). Omitting the transform echoes the 'auto' default too. A stored value
            OUTSIDE the valid set (only reachable on a config written before create-time validation existed) reads "invalid
            (<value>) — engine falls back to auto, resolved at train time", mirroring the engine's fallback rather than
            promising a transform it will not apply. Null for cross_sectional configs.
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
    auto_reduce: bool | Unset = False
    autoregressive: str | Unset = "full"
    backtest_config: None | PredictionConfigOutBacktestConfigType0 | Unset = UNSET
    baseline_mode: str | Unset = "neural"
    core_columns: list[str] | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    discovery_mode: bool | Unset = False
    error_message: None | str | Unset = UNSET
    eval_metric_config: None | PredictionConfigOutEvalMetricConfigType0 | Unset = UNSET
    feature_config: None | PredictionConfigOutFeatureConfigType0 | Unset = UNSET
    feature_fields: list[str] | None | Unset = UNSET
    frequency: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    max_ar_lag: int | None | Unset = UNSET
    min_history_years: float | None | Unset = UNSET
    min_rows: int | None | Unset = UNSET
    mode: str | Unset = "timeseries"
    neural_confidence_tau: float | Unset = 0.0
    objective: PredictionConfigOutObjective | Unset = PredictionConfigOutObjective.SKILL_VS_PERSISTENCE
    output_space: None | str | Unset = UNSET
    panel_sufficiency: None | PredictionConfigOutPanelSufficiencyType0 | Unset = UNSET
    reduction_manifest: None | PredictionConfigOutReductionManifestType0 | Unset = UNSET
    regime_platform_id: int | None | Unset = UNSET
    resolved_target_transform: None | str | Unset = UNSET
    target_transform_reason: None | str | Unset = UNSET
    time_index_field: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_config_out_backtest_config_type_0 import PredictionConfigOutBacktestConfigType0
        from ..models.prediction_config_out_eval_metric_config_type_0 import PredictionConfigOutEvalMetricConfigType0
        from ..models.prediction_config_out_feature_config_type_0 import PredictionConfigOutFeatureConfigType0
        from ..models.prediction_config_out_panel_sufficiency_type_0 import PredictionConfigOutPanelSufficiencyType0
        from ..models.prediction_config_out_reduction_manifest_type_0 import PredictionConfigOutReductionManifestType0

        eval_metric = self.eval_metric

        id = self.id

        model_tier = self.model_tier

        model_type = self.model_type

        organisation_id = self.organisation_id

        platform_id = self.platform_id

        status = self.status

        target_field = self.target_field

        auto_reduce = self.auto_reduce

        autoregressive = self.autoregressive

        backtest_config: dict[str, Any] | None | Unset
        if isinstance(self.backtest_config, Unset):
            backtest_config = UNSET
        elif isinstance(self.backtest_config, PredictionConfigOutBacktestConfigType0):
            backtest_config = self.backtest_config.to_dict()
        else:
            backtest_config = self.backtest_config

        baseline_mode = self.baseline_mode

        core_columns: list[str] | None | Unset
        if isinstance(self.core_columns, Unset):
            core_columns = UNSET
        elif isinstance(self.core_columns, list):
            core_columns = self.core_columns

        else:
            core_columns = self.core_columns

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        discovery_mode = self.discovery_mode

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        eval_metric_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_metric_config, Unset):
            eval_metric_config = UNSET
        elif isinstance(self.eval_metric_config, PredictionConfigOutEvalMetricConfigType0):
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

        min_history_years: float | None | Unset
        if isinstance(self.min_history_years, Unset):
            min_history_years = UNSET
        else:
            min_history_years = self.min_history_years

        min_rows: int | None | Unset
        if isinstance(self.min_rows, Unset):
            min_rows = UNSET
        else:
            min_rows = self.min_rows

        mode = self.mode

        neural_confidence_tau = self.neural_confidence_tau

        objective: str | Unset = UNSET
        if not isinstance(self.objective, Unset):
            objective = self.objective.value

        output_space: None | str | Unset
        if isinstance(self.output_space, Unset):
            output_space = UNSET
        else:
            output_space = self.output_space

        panel_sufficiency: dict[str, Any] | None | Unset
        if isinstance(self.panel_sufficiency, Unset):
            panel_sufficiency = UNSET
        elif isinstance(self.panel_sufficiency, PredictionConfigOutPanelSufficiencyType0):
            panel_sufficiency = self.panel_sufficiency.to_dict()
        else:
            panel_sufficiency = self.panel_sufficiency

        reduction_manifest: dict[str, Any] | None | Unset
        if isinstance(self.reduction_manifest, Unset):
            reduction_manifest = UNSET
        elif isinstance(self.reduction_manifest, PredictionConfigOutReductionManifestType0):
            reduction_manifest = self.reduction_manifest.to_dict()
        else:
            reduction_manifest = self.reduction_manifest

        regime_platform_id: int | None | Unset
        if isinstance(self.regime_platform_id, Unset):
            regime_platform_id = UNSET
        else:
            regime_platform_id = self.regime_platform_id

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
        if auto_reduce is not UNSET:
            field_dict["auto_reduce"] = auto_reduce
        if autoregressive is not UNSET:
            field_dict["autoregressive"] = autoregressive
        if backtest_config is not UNSET:
            field_dict["backtest_config"] = backtest_config
        if baseline_mode is not UNSET:
            field_dict["baseline_mode"] = baseline_mode
        if core_columns is not UNSET:
            field_dict["core_columns"] = core_columns
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if discovery_mode is not UNSET:
            field_dict["discovery_mode"] = discovery_mode
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
        if min_history_years is not UNSET:
            field_dict["min_history_years"] = min_history_years
        if min_rows is not UNSET:
            field_dict["min_rows"] = min_rows
        if mode is not UNSET:
            field_dict["mode"] = mode
        if neural_confidence_tau is not UNSET:
            field_dict["neural_confidence_tau"] = neural_confidence_tau
        if objective is not UNSET:
            field_dict["objective"] = objective
        if output_space is not UNSET:
            field_dict["output_space"] = output_space
        if panel_sufficiency is not UNSET:
            field_dict["panel_sufficiency"] = panel_sufficiency
        if reduction_manifest is not UNSET:
            field_dict["reduction_manifest"] = reduction_manifest
        if regime_platform_id is not UNSET:
            field_dict["regime_platform_id"] = regime_platform_id
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
        from ..models.prediction_config_out_backtest_config_type_0 import PredictionConfigOutBacktestConfigType0
        from ..models.prediction_config_out_eval_metric_config_type_0 import PredictionConfigOutEvalMetricConfigType0
        from ..models.prediction_config_out_feature_config_type_0 import PredictionConfigOutFeatureConfigType0
        from ..models.prediction_config_out_panel_sufficiency_type_0 import PredictionConfigOutPanelSufficiencyType0
        from ..models.prediction_config_out_reduction_manifest_type_0 import PredictionConfigOutReductionManifestType0

        d = dict(src_dict)
        eval_metric = d.pop("eval_metric")

        id = d.pop("id")

        model_tier = d.pop("model_tier")

        model_type = d.pop("model_type")

        organisation_id = d.pop("organisation_id")

        platform_id = d.pop("platform_id")

        status = d.pop("status")

        target_field = d.pop("target_field")

        auto_reduce = d.pop("auto_reduce", UNSET)

        autoregressive = d.pop("autoregressive", UNSET)

        def _parse_backtest_config(data: object) -> None | PredictionConfigOutBacktestConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backtest_config_type_0 = PredictionConfigOutBacktestConfigType0.from_dict(data)

                return backtest_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutBacktestConfigType0 | Unset, data)

        backtest_config = _parse_backtest_config(d.pop("backtest_config", UNSET))

        baseline_mode = d.pop("baseline_mode", UNSET)

        def _parse_core_columns(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                core_columns_type_0 = cast(list[str], data)

                return core_columns_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        core_columns = _parse_core_columns(d.pop("core_columns", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        discovery_mode = d.pop("discovery_mode", UNSET)

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_eval_metric_config(data: object) -> None | PredictionConfigOutEvalMetricConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_metric_config_type_0 = PredictionConfigOutEvalMetricConfigType0.from_dict(data)

                return eval_metric_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutEvalMetricConfigType0 | Unset, data)

        eval_metric_config = _parse_eval_metric_config(d.pop("eval_metric_config", UNSET))

        def _parse_feature_config(data: object) -> None | PredictionConfigOutFeatureConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_config_type_0 = PredictionConfigOutFeatureConfigType0.from_dict(data)

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

        def _parse_min_history_years(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        min_history_years = _parse_min_history_years(d.pop("min_history_years", UNSET))

        def _parse_min_rows(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        min_rows = _parse_min_rows(d.pop("min_rows", UNSET))

        mode = d.pop("mode", UNSET)

        neural_confidence_tau = d.pop("neural_confidence_tau", UNSET)

        _objective = d.pop("objective", UNSET)
        objective: PredictionConfigOutObjective | Unset
        if isinstance(_objective, Unset):
            objective = UNSET
        else:
            objective = PredictionConfigOutObjective(_objective)

        def _parse_output_space(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        output_space = _parse_output_space(d.pop("output_space", UNSET))

        def _parse_panel_sufficiency(data: object) -> None | PredictionConfigOutPanelSufficiencyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                panel_sufficiency_type_0 = PredictionConfigOutPanelSufficiencyType0.from_dict(data)

                return panel_sufficiency_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutPanelSufficiencyType0 | Unset, data)

        panel_sufficiency = _parse_panel_sufficiency(d.pop("panel_sufficiency", UNSET))

        def _parse_reduction_manifest(data: object) -> None | PredictionConfigOutReductionManifestType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                reduction_manifest_type_0 = PredictionConfigOutReductionManifestType0.from_dict(data)

                return reduction_manifest_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigOutReductionManifestType0 | Unset, data)

        reduction_manifest = _parse_reduction_manifest(d.pop("reduction_manifest", UNSET))

        def _parse_regime_platform_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        regime_platform_id = _parse_regime_platform_id(d.pop("regime_platform_id", UNSET))

        def _parse_resolved_target_transform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        resolved_target_transform = _parse_resolved_target_transform(d.pop("resolved_target_transform", UNSET))

        def _parse_target_transform_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        target_transform_reason = _parse_target_transform_reason(d.pop("target_transform_reason", UNSET))

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
            auto_reduce=auto_reduce,
            autoregressive=autoregressive,
            backtest_config=backtest_config,
            baseline_mode=baseline_mode,
            core_columns=core_columns,
            created_at=created_at,
            discovery_mode=discovery_mode,
            error_message=error_message,
            eval_metric_config=eval_metric_config,
            feature_config=feature_config,
            feature_fields=feature_fields,
            frequency=frequency,
            horizon=horizon,
            max_ar_lag=max_ar_lag,
            min_history_years=min_history_years,
            min_rows=min_rows,
            mode=mode,
            neural_confidence_tau=neural_confidence_tau,
            objective=objective,
            output_space=output_space,
            panel_sufficiency=panel_sufficiency,
            reduction_manifest=reduction_manifest,
            regime_platform_id=regime_platform_id,
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
