from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.prediction_config_create_objective import PredictionConfigCreateObjective
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.prediction_config_create_backtest_config_type_0 import PredictionConfigCreateBacktestConfigType0
    from ..models.prediction_config_create_eval_metric_config_type_0 import PredictionConfigCreateEvalMetricConfigType0
    from ..models.prediction_config_create_feature_config_type_0 import PredictionConfigCreateFeatureConfigType0


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
            auto_reduce (bool | Unset): Opt-in auto-reduction. When a declared min_rows/min_history_years bar is unmet at
                train time, instead of returning HTTP 409 sufficiency_gate_failed, the sparsest AUXILIARY columns (never
                core_columns, target_field, or time_index_field) are dropped one at a time until the bar is met. The reduced
                feature set is persisted to feature_fields and a reduction manifest (dropped columns + before/after usable rows)
                is returned on the train 202 body and readable back on the config. If the bar is UNREACHABLE even after dropping
                every auxiliary column, the 409 is still returned (fail-closed — this never trains on a sub-bar panel and never
                fills/fabricates values to meet the bar). Default False: old 409-only behaviour, byte-identical when unset.
                Default: False.
            autoregressive (str | Unset): Autoregression control (timeseries mode only) — how much the forecast may rely on
                the TARGET's own recent values. Plain-language framing: 'none' = Drivers only (default — no target-derived
                lag/roc/rolling features; explain purely through the other indicators); 'limited' = Drivers + a little history
                (only the most recent value / shortest target-history feature is allowed, so the drivers carry the explanation);
                'full' = History allowed (the target's own lags/rolling/rate-of-change features are available). Covariate
                (driver) features are NEVER restricted. The advanced 'max_ar_lag' overrides this. The effective setting is
                echoed in the model metadata of the predict response. Ignored in cross_sectional mode. Default: 'none'.
            backtest_config (None | PredictionConfigCreateBacktestConfigType0 | Unset): Backtesting configuration. Keys:
                'test_ratio' (float, default 0.2), 'n_splits' (int, default 1). In timeseries mode, uses expanding-window splits
                to prevent future leakage. In cross_sectional mode, uses stratified random splits.
            baseline_mode (str | Unset): Forecast anchor for the symbolic forecaster (timeseries mode only). Controls the
                reference model the forecast composes onto: 'neural' (default — GBT prediction through the S2 confidence gate
                for no-driver points; no_forecast when the platform has no trained model); 'persistence' (last observed level);
                'drift' (last level + h * OLS slope — a linear-trend anchor). The holdout acceptance gate recomposes driver
                effects onto the chosen anchor so they are not mis-scaled. skill_vs_persistence is ALWAYS reported as the
                external benchmark regardless of anchor. Ignored in cross_sectional mode. Default: 'neural'.
            core_columns (list[str] | None | Unset): Column-role declaration: columns that must NEVER be dropped by
                auto_reduce. The target_field and time_index_field are implicitly core regardless of this list. Every other
                candidate feature column is treated as AUXILIARY — droppable by auto_reduce, cheapest-information-cost
                (sparsest) first. Has no effect unless auto_reduce=true.
            eval_metric (None | str | Unset): Primary evaluation metric. Options: 'rmse' (root mean squared error), 'mae'
                (mean absolute error), 'r2' (R-squared), 'dir_accuracy' (directional accuracy — timeseries only). When null (the
                default), the metric is derived from the objective: skill_vs_persistence -> rmse;
                directional_pnl/sharpe_ratio/hit_rate -> dir_accuracy. An explicit value overrides the derivation.
            eval_metric_config (None | PredictionConfigCreateEvalMetricConfigType0 | Unset): Additional metric
                configuration. Reserved for future use.
            feature_config (None | PredictionConfigCreateFeatureConfigType0 | Unset): Advanced feature engineering
                configuration (timeseries mode only). Controls which derived features are generated. Keys: 'lags' (list[int]),
                'rolling_mean' (list[int]), 'rolling_std' (list[int]), 'roc' (list[int] — rate of change), 'seasonal_dummies'
                (bool), 'differencing' (bool), 'target_transform' (str: 'auto'|'none'|'difference'). target_transform controls
                how the forecast target is framed: 'auto' (default) differences a trending target automatically so a tree model
                is not asked to extrapolate a non-stationary level (which yields negative R²); 'none' forecasts the raw level;
                'difference' forecasts the change and reconstructs the level. The resolved transform (and why) is echoed in the
                model metadata of the predict response. UNKNOWN keys are rejected (422), not ignored. Defaults are frequency-
                dependent. Ignored in cross_sectional mode.
            feature_fields (list[str] | None | Unset): Explicit list of column names to use as input features. If null, all
                numeric columns (excluding the target and time index) are used automatically. In cross_sectional mode, these are
                the raw columns fed directly to the model. In timeseries mode, these are the base columns from which lag/rolling
                features are derived.
            frequency (None | str | Unset): Temporal granularity of the data. One of: 'daily', 'weekly', 'monthly',
                'quarterly'. Determines default lag/rolling window sizes in timeseries mode. Omit for cross_sectional mode.
            horizon (int | None | Unset): Number of steps ahead to forecast. Only meaningful in timeseries mode — e.g.
                horizon=3 with frequency='monthly' predicts 3 months ahead. Omit or set to null for cross_sectional mode.
            max_ar_lag (int | None | Unset): Advanced numeric override for autoregression control (timeseries mode only).
                When set, OVERRIDES 'autoregressive': 0 = no target-derived lag/roc/rolling features (drivers only); k = allow
                target-history features with lag/window/period <= k. null (default) = defer to the 'autoregressive' enum.
                Covariate features are never restricted. Ignored in cross_sectional mode.
            min_history_years (float | None | Unset): Minimum history span (in years) required for training (sufficiency
                gate).  When set, the train endpoint checks the ACTUAL date span of the post-warmup data and returns a
                structured HTTP 409 sufficiency_gate_failed if the span is too short.  None (the default) disables the gate.
            min_rows (int | None | Unset): Minimum post-warmup row count required for training (sufficiency gate).  When
                set, the train endpoint checks the ACTUAL row count after feature engineering (lag/rolling dropna) and returns a
                structured HTTP 409 sufficiency_gate_failed if the data falls short.  The 409 payload names the shortfall and
                the recovery_groups cut-list from the panel report.  None (the default) disables the gate — old path byte-
                identical.
            mode (str | Unset): Prediction mode. 'timeseries' learns temporal patterns (lags, rolling windows, seasonality)
                and forecasts future values. 'cross_sectional' treats each row independently and learns a direct feature-to-
                target mapping. Default: 'timeseries'. Default: 'timeseries'.
            model_tier (str | Unset): Model complexity tier. Currently only 'tier1' is supported: the built-in registry
                (sklearn GBT/ridge/lasso + CPU-trainable PyTorch LSTM/Transformer). Default: 'tier1'.
            model_type (str | Unset): Algorithm to use. Options: 'auto' (default — trains all five candidate models and
                selects the winner by eval_metric on the validation split; the winning model type and per-candidate scores are
                recorded in the metrics payload), 'gbt' (Gradient Boosted Trees), 'ridge' (L2-regularised linear), 'lasso'
                (L1-regularised linear, good for sparse features), 'lstm' (LSTM recurrent network — slower to train, CPU-
                viable), 'transformer' (Transformer encoder — slower to train, CPU-viable). LSTM/Transformer train in ~200
                epochs on CPU; training is async (202 + poll) so the cost is wall-clock, not request-blocking. Default: 'auto'.
            neural_confidence_tau (float | Unset): Per-point neural-tier confidence threshold (timeseries mode only). The
                GBT prediction is admitted as 'neural_scored' when its two-axis confidence (Axis A: in-training-range OOD gate +
                Axis B: interval sharpness) >= tau. Below tau the raw GBT prediction is still served with tier 'neural_weak' and
                the full confidence certificate. Default 0.0 (gate labels every prediction with its tier and confidence; set > 0
                to distinguish strong vs weak neural predictions). Default: 0.0.
            objective (PredictionConfigCreateObjective | Unset): Optimisation objective selection. The chosen objective is
                stored on the config and the corresponding trading metric is computed and reported in backtest results. NOTE:
                the configured objective currently does not drive rule acceptance; skill_vs_persistence remains the acceptance
                criterion regardless of this setting. Options: 'skill_vs_persistence' (default — forecast skill relative to a
                naive persist-last-value baseline), 'directional_pnl' (cumulative directional PnL on the holdout),
                'sharpe_ratio' (annualised Sharpe of the directional PnL stream), 'hit_rate' (directional hit rate excluding
                zero-actual-move periods). Trading objectives (pnl/sharpe/hit_rate) require a frequency on the config for
                annualisation. Default: PredictionConfigCreateObjective.SKILL_VS_PERSISTENCE.
            regime_platform_id (int | None | Unset): ID of a Decisions platform (same org) that classifies macro regimes. At
                build time the panel is batch-classified via this platform and regime labels are injected as one-hot dummy
                features (regime_<label>). The symbolic forecaster can then learn regime-conditional rules. At forecast time a
                live single-classify of the current observation is performed and the regime provenance (label + proof
                certificate) is returned on the payload. Null (default) = no regime conditioning.
            target_transform (None | str | Unset): Top-level shorthand for feature_config['target_transform'] (timeseries
                mode only). One of 'auto' (the default when omitted) | 'none' | 'difference'; an unknown value is rejected with
                422 naming the valid set. Equivalent to nesting the same value under feature_config — when BOTH are supplied the
                NESTED value wins and the conflict is logged, but the LOSING value is still validated, so an out-of-set spelling
                can never vanish behind the precedence rule. Ignored in cross_sectional mode.
            time_index_field (None | str | Unset): Column containing date/time values used to order observations. Required
                for timeseries mode (e.g. 'date', 'observation_month'). Must be omitted or null for cross_sectional mode — rows
                have no temporal ordering.
    """

    target_field: str
    auto_reduce: bool | Unset = False
    autoregressive: str | Unset = "none"
    backtest_config: None | PredictionConfigCreateBacktestConfigType0 | Unset = UNSET
    baseline_mode: str | Unset = "neural"
    core_columns: list[str] | None | Unset = UNSET
    eval_metric: None | str | Unset = UNSET
    eval_metric_config: None | PredictionConfigCreateEvalMetricConfigType0 | Unset = UNSET
    feature_config: None | PredictionConfigCreateFeatureConfigType0 | Unset = UNSET
    feature_fields: list[str] | None | Unset = UNSET
    frequency: None | str | Unset = UNSET
    horizon: int | None | Unset = UNSET
    max_ar_lag: int | None | Unset = UNSET
    min_history_years: float | None | Unset = UNSET
    min_rows: int | None | Unset = UNSET
    mode: str | Unset = "timeseries"
    model_tier: str | Unset = "tier1"
    model_type: str | Unset = "auto"
    neural_confidence_tau: float | Unset = 0.0
    objective: PredictionConfigCreateObjective | Unset = PredictionConfigCreateObjective.SKILL_VS_PERSISTENCE
    regime_platform_id: int | None | Unset = UNSET
    target_transform: None | str | Unset = UNSET
    time_index_field: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.prediction_config_create_backtest_config_type_0 import PredictionConfigCreateBacktestConfigType0
        from ..models.prediction_config_create_eval_metric_config_type_0 import (
            PredictionConfigCreateEvalMetricConfigType0,
        )
        from ..models.prediction_config_create_feature_config_type_0 import PredictionConfigCreateFeatureConfigType0

        target_field = self.target_field

        auto_reduce = self.auto_reduce

        autoregressive = self.autoregressive

        backtest_config: dict[str, Any] | None | Unset
        if isinstance(self.backtest_config, Unset):
            backtest_config = UNSET
        elif isinstance(self.backtest_config, PredictionConfigCreateBacktestConfigType0):
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

        eval_metric: None | str | Unset
        if isinstance(self.eval_metric, Unset):
            eval_metric = UNSET
        else:
            eval_metric = self.eval_metric

        eval_metric_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_metric_config, Unset):
            eval_metric_config = UNSET
        elif isinstance(self.eval_metric_config, PredictionConfigCreateEvalMetricConfigType0):
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

        model_tier = self.model_tier

        model_type = self.model_type

        neural_confidence_tau = self.neural_confidence_tau

        objective: str | Unset = UNSET
        if not isinstance(self.objective, Unset):
            objective = self.objective.value

        regime_platform_id: int | None | Unset
        if isinstance(self.regime_platform_id, Unset):
            regime_platform_id = UNSET
        else:
            regime_platform_id = self.regime_platform_id

        target_transform: None | str | Unset
        if isinstance(self.target_transform, Unset):
            target_transform = UNSET
        else:
            target_transform = self.target_transform

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
        if max_ar_lag is not UNSET:
            field_dict["max_ar_lag"] = max_ar_lag
        if min_history_years is not UNSET:
            field_dict["min_history_years"] = min_history_years
        if min_rows is not UNSET:
            field_dict["min_rows"] = min_rows
        if mode is not UNSET:
            field_dict["mode"] = mode
        if model_tier is not UNSET:
            field_dict["model_tier"] = model_tier
        if model_type is not UNSET:
            field_dict["model_type"] = model_type
        if neural_confidence_tau is not UNSET:
            field_dict["neural_confidence_tau"] = neural_confidence_tau
        if objective is not UNSET:
            field_dict["objective"] = objective
        if regime_platform_id is not UNSET:
            field_dict["regime_platform_id"] = regime_platform_id
        if target_transform is not UNSET:
            field_dict["target_transform"] = target_transform
        if time_index_field is not UNSET:
            field_dict["time_index_field"] = time_index_field

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.prediction_config_create_backtest_config_type_0 import PredictionConfigCreateBacktestConfigType0
        from ..models.prediction_config_create_eval_metric_config_type_0 import (
            PredictionConfigCreateEvalMetricConfigType0,
        )
        from ..models.prediction_config_create_feature_config_type_0 import PredictionConfigCreateFeatureConfigType0

        d = dict(src_dict)
        target_field = d.pop("target_field")

        auto_reduce = d.pop("auto_reduce", UNSET)

        autoregressive = d.pop("autoregressive", UNSET)

        def _parse_backtest_config(data: object) -> None | PredictionConfigCreateBacktestConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                backtest_config_type_0 = PredictionConfigCreateBacktestConfigType0.from_dict(data)

                return backtest_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigCreateBacktestConfigType0 | Unset, data)

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

        def _parse_eval_metric(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        eval_metric = _parse_eval_metric(d.pop("eval_metric", UNSET))

        def _parse_eval_metric_config(data: object) -> None | PredictionConfigCreateEvalMetricConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_metric_config_type_0 = PredictionConfigCreateEvalMetricConfigType0.from_dict(data)

                return eval_metric_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PredictionConfigCreateEvalMetricConfigType0 | Unset, data)

        eval_metric_config = _parse_eval_metric_config(d.pop("eval_metric_config", UNSET))

        def _parse_feature_config(data: object) -> None | PredictionConfigCreateFeatureConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_config_type_0 = PredictionConfigCreateFeatureConfigType0.from_dict(data)

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

        model_tier = d.pop("model_tier", UNSET)

        model_type = d.pop("model_type", UNSET)

        neural_confidence_tau = d.pop("neural_confidence_tau", UNSET)

        _objective = d.pop("objective", UNSET)
        objective: PredictionConfigCreateObjective | Unset
        if isinstance(_objective, Unset):
            objective = UNSET
        else:
            objective = PredictionConfigCreateObjective(_objective)

        def _parse_regime_platform_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        regime_platform_id = _parse_regime_platform_id(d.pop("regime_platform_id", UNSET))

        def _parse_target_transform(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        target_transform = _parse_target_transform(d.pop("target_transform", UNSET))

        def _parse_time_index_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time_index_field = _parse_time_index_field(d.pop("time_index_field", UNSET))

        prediction_config_create = cls(
            target_field=target_field,
            auto_reduce=auto_reduce,
            autoregressive=autoregressive,
            backtest_config=backtest_config,
            baseline_mode=baseline_mode,
            core_columns=core_columns,
            eval_metric=eval_metric,
            eval_metric_config=eval_metric_config,
            feature_config=feature_config,
            feature_fields=feature_fields,
            frequency=frequency,
            horizon=horizon,
            max_ar_lag=max_ar_lag,
            min_history_years=min_history_years,
            min_rows=min_rows,
            mode=mode,
            model_tier=model_tier,
            model_type=model_type,
            neural_confidence_tau=neural_confidence_tau,
            objective=objective,
            regime_platform_id=regime_platform_id,
            target_transform=target_transform,
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
