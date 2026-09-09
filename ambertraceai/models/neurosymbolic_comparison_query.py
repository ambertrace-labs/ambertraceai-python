from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.neurosymbolic_comparison_query_feature_overrides_type_0 import (
        NeurosymbolicComparisonQueryFeatureOverridesType0,
    )


T = TypeVar("T", bound="NeurosymbolicComparisonQuery")


@_attrs_define
class NeurosymbolicComparisonQuery:
    """Request body for the neural-vs-neurosymbolic comparison.

    The comparison scores BOTH branches against KNOWN historical actuals over
    the expanding-window holdout (the backtest is NEVER overridden).  When
    ``feature_overrides`` is supplied, a FORWARD what-if projection is
    computed alongside the backtest: the overrides are injected into the latest
    data row and propagated through the neural+symbolic forward forecast.  The
    response carries both the forward what-if result and the backtest impact
    information side-by-side (``forward_whatif`` + ``backtest_impact``).

        Attributes:
            prediction_config_id (int): The timeseries prediction config to compare. Neural metrics are computed from the
                model alone; neurosymbolic metrics apply the platform's active adjustment+constraint rules over the same
                holdout.
            feature_overrides (NeurosymbolicComparisonQueryFeatureOverridesType0 | None | Unset): Optional map of raw column
                name -> what-if value for the FORWARD projection. Overrides are injected into the latest data row and propagated
                through engineered features (lags, rolling means) for the forward forecast ONLY — the backtest scoring path is
                NEVER overridden. The response carries the forward what-if result under 'forward_whatif' alongside the backtest
                impact under 'backtest_impact'. Omit (or null) for a backtest-only comparison (backward-compatible).
            include_pending (bool | Unset): When true, the neurosymbolic branch ALSO applies the accepted-but-pending
                discovered rules for this config (a read-only 'what-if' preview of the discovered set BEFORE the human approval
                gate). is_active is never mutated. The result carries mode='preview_pending' and n_pending_rules. Default false:
                active rules only (the shipped delta). Default: False.
            include_series (bool | Unset): When true, the completed job result ALSO carries a 'series' array — the per-
                period neural-vs-neurosymbolic head-to-head over the SAME held-out backtest points the aggregate metrics are
                computed from, so the comparison can be charted OVER TIME. Each entry is {index (position in the engineered
                holdout), time (ISO-8601 period, when the config has a usable time_index_field), actual (the realised level
                target), neural (the model-only level prediction), neurosymbolic (the prediction after the rules are applied),
                rule_fired (true iff applying the rules CHANGED the prediction for that period — i.e. neural != neurosymbolic)}.
                The series reconciles with the aggregate metrics (it is the same computation, not a recompute). Honours
                include_pending (the preview series applies the pending rules too). Default false: the 'series' field is omitted
                entirely (additive / back-compatible). Default: False.
    """

    prediction_config_id: int
    feature_overrides: NeurosymbolicComparisonQueryFeatureOverridesType0 | None | Unset = UNSET
    include_pending: bool | Unset = False
    include_series: bool | Unset = False
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.neurosymbolic_comparison_query_feature_overrides_type_0 import (
            NeurosymbolicComparisonQueryFeatureOverridesType0,
        )

        prediction_config_id = self.prediction_config_id

        feature_overrides: dict[str, Any] | None | Unset
        if isinstance(self.feature_overrides, Unset):
            feature_overrides = UNSET
        elif isinstance(self.feature_overrides, NeurosymbolicComparisonQueryFeatureOverridesType0):
            feature_overrides = self.feature_overrides.to_dict()
        else:
            feature_overrides = self.feature_overrides

        include_pending = self.include_pending

        include_series = self.include_series

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prediction_config_id": prediction_config_id,
            }
        )
        if feature_overrides is not UNSET:
            field_dict["feature_overrides"] = feature_overrides
        if include_pending is not UNSET:
            field_dict["include_pending"] = include_pending
        if include_series is not UNSET:
            field_dict["include_series"] = include_series

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.neurosymbolic_comparison_query_feature_overrides_type_0 import (
            NeurosymbolicComparisonQueryFeatureOverridesType0,
        )

        d = dict(src_dict)
        prediction_config_id = d.pop("prediction_config_id")

        def _parse_feature_overrides(data: object) -> NeurosymbolicComparisonQueryFeatureOverridesType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                feature_overrides_type_0 = NeurosymbolicComparisonQueryFeatureOverridesType0.from_dict(data)

                return feature_overrides_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(NeurosymbolicComparisonQueryFeatureOverridesType0 | None | Unset, data)

        feature_overrides = _parse_feature_overrides(d.pop("feature_overrides", UNSET))

        include_pending = d.pop("include_pending", UNSET)

        include_series = d.pop("include_series", UNSET)

        neurosymbolic_comparison_query = cls(
            prediction_config_id=prediction_config_id,
            feature_overrides=feature_overrides,
            include_pending=include_pending,
            include_series=include_series,
        )

        neurosymbolic_comparison_query.additional_properties = d
        return neurosymbolic_comparison_query

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
