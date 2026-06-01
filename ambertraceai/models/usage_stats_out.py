from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.token_budget_out import TokenBudgetOut


T = TypeVar("T", bound="UsageStatsOut")


@_attrs_define
class UsageStatsOut:
    """
    Attributes:
        avg_response_time_ms (float):
        period_days (int):
        total_requests (int):
        total_tokens (int):
        token_budget (None | TokenBudgetOut | Unset):
    """

    avg_response_time_ms: float
    period_days: int
    total_requests: int
    total_tokens: int
    token_budget: None | TokenBudgetOut | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.token_budget_out import TokenBudgetOut

        avg_response_time_ms = self.avg_response_time_ms

        period_days = self.period_days

        total_requests = self.total_requests

        total_tokens = self.total_tokens

        token_budget: dict[str, Any] | None | Unset
        if isinstance(self.token_budget, Unset):
            token_budget = UNSET
        elif isinstance(self.token_budget, TokenBudgetOut):
            token_budget = self.token_budget.to_dict()
        else:
            token_budget = self.token_budget

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "avg_response_time_ms": avg_response_time_ms,
                "period_days": period_days,
                "total_requests": total_requests,
                "total_tokens": total_tokens,
            }
        )
        if token_budget is not UNSET:
            field_dict["token_budget"] = token_budget

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.token_budget_out import TokenBudgetOut

        d = dict(src_dict)
        avg_response_time_ms = d.pop("avg_response_time_ms")

        period_days = d.pop("period_days")

        total_requests = d.pop("total_requests")

        total_tokens = d.pop("total_tokens")

        def _parse_token_budget(data: object) -> None | TokenBudgetOut | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                token_budget_type_0 = TokenBudgetOut.from_dict(data)

                return token_budget_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TokenBudgetOut | Unset, data)

        token_budget = _parse_token_budget(d.pop("token_budget", UNSET))

        usage_stats_out = cls(
            avg_response_time_ms=avg_response_time_ms,
            period_days=period_days,
            total_requests=total_requests,
            total_tokens=total_tokens,
            token_budget=token_budget,
        )

        usage_stats_out.additional_properties = d
        return usage_stats_out

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
