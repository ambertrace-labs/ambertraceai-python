from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.symbolic_forecast_request_feature_overrides_type_0 import SymbolicForecastRequestFeatureOverridesType0


T = TypeVar("T", bound="SymbolicForecastRequest")


@_attrs_define
class SymbolicForecastRequest:
    """Request body for the symbolic-forecast "why" endpoint.

    Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction
    config's dataset: it induces human-readable driver-rules over the dataset's
    REAL features and composes the forecast as ``baseline + Σ fired drivers``, so
    the response carries an actionable *why* (the ordered drivers + their fitted
    contributions + reliability), not just a number. With ``verified=true`` the
    active-driver set is run through the verified kernel and each driver is
    stamped ``proof_checked``.

        Attributes:
            prediction_config_id (int): ID of a prediction config on this platform. The config supplies the target_field,
                time_index_field, horizon, and feature_fields the forecaster fits over. The config need NOT be trained (the
                symbolic forecaster is independent of the trained neural model).
            as_of (None | str | Unset): The forecast period — the ALIGNMENT KEY every consuming decision must share. A
                downstream decision fanning in several predictions fails closed on a mismatched-period or missing named model.
                Free-form period label (e.g. an ISO date '2026-06-30' or a period tag).
            compact_certification (bool | Unset): Payload slimming, COMPACT BY DEFAULT as of 0.19.0 (the breaking flip
                announced in 0.18.0). When true (the DEFAULT), the top-level 'why_certification' per-feature 'certified_facts'
                list (one certificate per engineered feature — ~124 KB for a wide panel) is REPLACED by a compact
                'certification_summary' {proof_checked, n_certified, n_rejected, min_confidence}; proof_ref + the proof summary
                are retained, and the full list stays retrievable from the persisted record store by (model_id, as_of). Pass
                compact_certification=False to opt BACK IN to the full 'certified_facts' list at the top level. The embedded
                'prediction_record.why_certification' ALWAYS carries the compact handle form (proof_checked + proof_summary +
                certification_summary) regardless of this flag — the record is a proof-carrying handle, not a second copy of the
                fact list (double-embed de-dup); a downstream decision re-checks the handle, never the embedded facts. Default:
                True.
            entity (None | str | Unset): Optional join key on the PredictionRecord (entity).
            feature_overrides (None | SymbolicForecastRequestFeatureOverridesType0 | Unset): Optional map of raw column name
                -> what-if value applied to the most recent row before composing the forecast (e.g. {'inflation': 5.0}). Lets a
                trader/C2 ask 'which drivers fire, and where does the forecast move, if feature X were Y?'. Omit to forecast
                from the latest data.
            include_fitted_series (bool | Unset): When true, ALSO return the backtest's per-period fitted-vs-actual
                TIMESERIES under 'fitted_series' so a consumer can chart actual vs symbolic-rules-fitted over history. This is
                the SAME walk the skill_vs_persistence metric is computed from — no extra fit. Each point is {index
                (date/position of the realised period), actual (observed value), predicted (baseline + Σ fired driver
                contributions), persistence (the predict-last-level baseline)}. HONEST LABEL: the series 'basis' is
                'walk_forward_out_of_sample_one_step' — the drivers were induced + accepted on the FIT window only and held
                FROZEN across the holdout, so each period's prediction never saw that period's outcome (the rigorous out-of-
                sample fit, NOT an in-sample fit). For a cross_sectional config rows are independent: the basis is
                'k_fold_cross_validation' (one held-out K-fold fold; no lag/rolling drivers, no persistence,
                skill_vs_persistence is null). The response also carries a 'coverage_certificate' whose TOTALITY claim (every
                holdout point served by a named tier with a finite value) is KERNEL-CERTIFIED: 'proof_ref' carries the trusted
                symbolic kernel's verdict with claim='coverage_totality' — an uncovered point fails the proof closed. Values
                remain fitted-not-proven. Off by default so the standard response is not bloated. Default: False.
            period (None | str | Unset): Optional join key on the PredictionRecord (period).
            prediction_model_id (None | str | Unset): Stable id for the emitted PredictionRecord (defaults to
                prediction_name / target_field). Used with as_of as the persisted-record key.
            prediction_name (None | str | Unset): Semantic role handle for the emitted PredictionRecord, e.g. 'ust_10y' or
                'ig_spread'. A downstream decision addresses this model by this name in a keyed predictions={role: record} fan-
                in. Defaults to the config's target_field when omitted.
            sector (None | str | Unset): Optional join key on the PredictionRecord (sector).
            top_drivers_n (int | None | Unset): Number of top drivers to surface in the PredictionRecord's ranked
                symbolic+neural list. Defaults to 5 when omitted.
            verified (bool | Unset): When true, run the current feature row through the verified kernel so the active-driver
                set is proof-carrying: each driver in the WHY is stamped with 'proof_checked' and the response carries a
                'why_certification' block (the certified facts, any rejected facts, the proof, and a human-readable summary).
                The fitted magnitudes/bands remain statistical (outside the proof) either way. Default: False.
    """

    prediction_config_id: int
    as_of: None | str | Unset = UNSET
    compact_certification: bool | Unset = True
    entity: None | str | Unset = UNSET
    feature_overrides: None | SymbolicForecastRequestFeatureOverridesType0 | Unset = UNSET
    include_fitted_series: bool | Unset = False
    period: None | str | Unset = UNSET
    prediction_model_id: None | str | Unset = UNSET
    prediction_name: None | str | Unset = UNSET
    sector: None | str | Unset = UNSET
    top_drivers_n: int | None | Unset = UNSET
    verified: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.symbolic_forecast_request_feature_overrides_type_0 import (
            SymbolicForecastRequestFeatureOverridesType0,
        )

        prediction_config_id = self.prediction_config_id

        as_of: None | str | Unset
        if isinstance(self.as_of, Unset):
            as_of = UNSET
        else:
            as_of = self.as_of

        compact_certification = self.compact_certification

        entity: None | str | Unset
        if isinstance(self.entity, Unset):
            entity = UNSET
        else:
            entity = self.entity

        feature_overrides: dict[str, Any] | None | Unset
        if isinstance(self.feature_overrides, Unset):
            feature_overrides = UNSET
        elif isinstance(self.feature_overrides, SymbolicForecastRequestFeatureOverridesType0):
            feature_overrides = self.feature_overrides.to_dict()
        else:
            feature_overrides = self.feature_overrides

        include_fitted_series = self.include_fitted_series

        period: None | str | Unset
        if isinstance(self.period, Unset):
            period = UNSET
        else:
            period = self.period

        prediction_model_id: None | str | Unset
        if isinstance(self.prediction_model_id, Unset):
            prediction_model_id = UNSET
        else:
            prediction_model_id = self.prediction_model_id

        prediction_name: None | str | Unset
        if isinstance(self.prediction_name, Unset):
            prediction_name = UNSET
        else:
            prediction_name = self.prediction_name

        sector: None | str | Unset
        if isinstance(self.sector, Unset):
            sector = UNSET
        else:
            sector = self.sector

        top_drivers_n: int | None | Unset
        if isinstance(self.top_drivers_n, Unset):
            top_drivers_n = UNSET
        else:
            top_drivers_n = self.top_drivers_n

        verified = self.verified

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prediction_config_id": prediction_config_id,
            }
        )
        if as_of is not UNSET:
            field_dict["as_of"] = as_of
        if compact_certification is not UNSET:
            field_dict["compact_certification"] = compact_certification
        if entity is not UNSET:
            field_dict["entity"] = entity
        if feature_overrides is not UNSET:
            field_dict["feature_overrides"] = feature_overrides
        if include_fitted_series is not UNSET:
            field_dict["include_fitted_series"] = include_fitted_series
        if period is not UNSET:
            field_dict["period"] = period
        if prediction_model_id is not UNSET:
            field_dict["prediction_model_id"] = prediction_model_id
        if prediction_name is not UNSET:
            field_dict["prediction_name"] = prediction_name
        if sector is not UNSET:
            field_dict["sector"] = sector
        if top_drivers_n is not UNSET:
            field_dict["top_drivers_n"] = top_drivers_n
        if verified is not UNSET:
            field_dict["verified"] = verified

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.symbolic_forecast_request_feature_overrides_type_0 import (
            SymbolicForecastRequestFeatureOverridesType0,
        )

        d = dict(src_dict)
        prediction_config_id = d.pop("prediction_config_id")

        def _parse_as_of(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        as_of = _parse_as_of(d.pop("as_of", UNSET))

        compact_certification = d.pop("compact_certification", UNSET)

        def _parse_entity(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        entity = _parse_entity(d.pop("entity", UNSET))

        def _parse_feature_overrides(data: object) -> None | SymbolicForecastRequestFeatureOverridesType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_overrides_type_0 = SymbolicForecastRequestFeatureOverridesType0.from_dict(data)

                return feature_overrides_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SymbolicForecastRequestFeatureOverridesType0 | Unset, data)

        feature_overrides = _parse_feature_overrides(d.pop("feature_overrides", UNSET))

        include_fitted_series = d.pop("include_fitted_series", UNSET)

        def _parse_period(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        period = _parse_period(d.pop("period", UNSET))

        def _parse_prediction_model_id(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        prediction_model_id = _parse_prediction_model_id(d.pop("prediction_model_id", UNSET))

        def _parse_prediction_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        prediction_name = _parse_prediction_name(d.pop("prediction_name", UNSET))

        def _parse_sector(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        sector = _parse_sector(d.pop("sector", UNSET))

        def _parse_top_drivers_n(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        top_drivers_n = _parse_top_drivers_n(d.pop("top_drivers_n", UNSET))

        verified = d.pop("verified", UNSET)

        symbolic_forecast_request = cls(
            prediction_config_id=prediction_config_id,
            as_of=as_of,
            compact_certification=compact_certification,
            entity=entity,
            feature_overrides=feature_overrides,
            include_fitted_series=include_fitted_series,
            period=period,
            prediction_model_id=prediction_model_id,
            prediction_name=prediction_name,
            sector=sector,
            top_drivers_n=top_drivers_n,
            verified=verified,
        )

        symbolic_forecast_request.additional_properties = d
        return symbolic_forecast_request

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
