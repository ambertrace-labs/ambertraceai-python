from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.feedback_stats_out_by_backend import FeedbackStatsOutByBackend
    from ..models.feedback_stats_out_by_category import FeedbackStatsOutByCategory
    from ..models.feedback_stats_out_by_decision import FeedbackStatsOutByDecision
    from ..models.feedback_stats_out_by_template import FeedbackStatsOutByTemplate


T = TypeVar("T", bound="FeedbackStatsOut")


@_attrs_define
class FeedbackStatsOut:
    """
    Attributes:
        by_backend (FeedbackStatsOutByBackend | Unset):
        by_category (FeedbackStatsOutByCategory | Unset):
        by_decision (FeedbackStatsOutByDecision | Unset):
        by_template (FeedbackStatsOutByTemplate | Unset):
        with_reason (int | Unset):  Default: 0.
    """

    by_backend: FeedbackStatsOutByBackend | Unset = UNSET
    by_category: FeedbackStatsOutByCategory | Unset = UNSET
    by_decision: FeedbackStatsOutByDecision | Unset = UNSET
    by_template: FeedbackStatsOutByTemplate | Unset = UNSET
    with_reason: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        by_backend: dict[str, Any] | Unset = UNSET
        if not isinstance(self.by_backend, Unset):
            by_backend = self.by_backend.to_dict()

        by_category: dict[str, Any] | Unset = UNSET
        if not isinstance(self.by_category, Unset):
            by_category = self.by_category.to_dict()

        by_decision: dict[str, Any] | Unset = UNSET
        if not isinstance(self.by_decision, Unset):
            by_decision = self.by_decision.to_dict()

        by_template: dict[str, Any] | Unset = UNSET
        if not isinstance(self.by_template, Unset):
            by_template = self.by_template.to_dict()

        with_reason = self.with_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if by_backend is not UNSET:
            field_dict["by_backend"] = by_backend
        if by_category is not UNSET:
            field_dict["by_category"] = by_category
        if by_decision is not UNSET:
            field_dict["by_decision"] = by_decision
        if by_template is not UNSET:
            field_dict["by_template"] = by_template
        if with_reason is not UNSET:
            field_dict["with_reason"] = with_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.feedback_stats_out_by_backend import FeedbackStatsOutByBackend
        from ..models.feedback_stats_out_by_category import FeedbackStatsOutByCategory
        from ..models.feedback_stats_out_by_decision import FeedbackStatsOutByDecision
        from ..models.feedback_stats_out_by_template import FeedbackStatsOutByTemplate

        d = dict(src_dict)
        _by_backend = d.pop("by_backend", UNSET)
        by_backend: FeedbackStatsOutByBackend | Unset
        if isinstance(_by_backend, Unset):
            by_backend = UNSET
        else:
            by_backend = FeedbackStatsOutByBackend.from_dict(_by_backend)

        _by_category = d.pop("by_category", UNSET)
        by_category: FeedbackStatsOutByCategory | Unset
        if isinstance(_by_category, Unset):
            by_category = UNSET
        else:
            by_category = FeedbackStatsOutByCategory.from_dict(_by_category)

        _by_decision = d.pop("by_decision", UNSET)
        by_decision: FeedbackStatsOutByDecision | Unset
        if isinstance(_by_decision, Unset):
            by_decision = UNSET
        else:
            by_decision = FeedbackStatsOutByDecision.from_dict(_by_decision)

        _by_template = d.pop("by_template", UNSET)
        by_template: FeedbackStatsOutByTemplate | Unset
        if isinstance(_by_template, Unset):
            by_template = UNSET
        else:
            by_template = FeedbackStatsOutByTemplate.from_dict(_by_template)

        with_reason = d.pop("with_reason", UNSET)

        feedback_stats_out = cls(
            by_backend=by_backend,
            by_category=by_category,
            by_decision=by_decision,
            by_template=by_template,
            with_reason=with_reason,
        )

        feedback_stats_out.additional_properties = d
        return feedback_stats_out

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
