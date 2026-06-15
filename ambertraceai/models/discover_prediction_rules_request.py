from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DiscoverPredictionRulesRequest")


@_attrs_define
class DiscoverPredictionRulesRequest:
    """Request body for triggering prediction rule discovery.

    Discovery analyses the trained model's residuals, generates corrective rule
    candidates (template-driven + LLM-parameterised), and A/B tests each against
    the expanding-window backtest. Accepted rules are stored pending expert
    approval (``is_active=False``). Runs in the background — the route returns 202.

        Attributes:
            prediction_config_id (int): ID of a trained prediction config on this platform. Discovery runs against this
                config's active model and residuals.
            max_rounds (int | None | Unset): Maximum discovery iterations. Each round proposes candidates and A/B tests
                them; the loop stops early when a round accepts nothing. Default: 3.
    """

    prediction_config_id: int
    max_rounds: int | None | Unset = 3
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        prediction_config_id = self.prediction_config_id

        max_rounds: int | None | Unset
        if isinstance(self.max_rounds, Unset):
            max_rounds = UNSET
        else:
            max_rounds = self.max_rounds

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prediction_config_id": prediction_config_id,
            }
        )
        if max_rounds is not UNSET:
            field_dict["max_rounds"] = max_rounds

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        prediction_config_id = d.pop("prediction_config_id")

        def _parse_max_rounds(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        max_rounds = _parse_max_rounds(d.pop("max_rounds", UNSET))

        discover_prediction_rules_request = cls(
            prediction_config_id=prediction_config_id,
            max_rounds=max_rounds,
        )

        discover_prediction_rules_request.additional_properties = d
        return discover_prediction_rules_request

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
