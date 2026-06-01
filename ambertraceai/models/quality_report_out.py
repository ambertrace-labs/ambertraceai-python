from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quality_report_out_completeness import QualityReportOutCompleteness
    from ..models.quality_report_out_consistency import QualityReportOutConsistency
    from ..models.quality_report_out_uniqueness import QualityReportOutUniqueness


T = TypeVar("T", bound="QualityReportOut")


@_attrs_define
class QualityReportOut:
    """
    Attributes:
        column_count (int):
        completeness (QualityReportOutCompleteness):
        consistency (QualityReportOutConsistency):
        overall_score (float):
        row_count (int):
        uniqueness (QualityReportOutUniqueness):
        recommendations (list[str] | Unset):
    """

    column_count: int
    completeness: QualityReportOutCompleteness
    consistency: QualityReportOutConsistency
    overall_score: float
    row_count: int
    uniqueness: QualityReportOutUniqueness
    recommendations: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        column_count = self.column_count

        completeness = self.completeness.to_dict()

        consistency = self.consistency.to_dict()

        overall_score = self.overall_score

        row_count = self.row_count

        uniqueness = self.uniqueness.to_dict()

        recommendations: list[str] | Unset = UNSET
        if not isinstance(self.recommendations, Unset):
            recommendations = self.recommendations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "column_count": column_count,
                "completeness": completeness,
                "consistency": consistency,
                "overall_score": overall_score,
                "row_count": row_count,
                "uniqueness": uniqueness,
            }
        )
        if recommendations is not UNSET:
            field_dict["recommendations"] = recommendations

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quality_report_out_completeness import (
            QualityReportOutCompleteness,
        )
        from ..models.quality_report_out_consistency import QualityReportOutConsistency
        from ..models.quality_report_out_uniqueness import QualityReportOutUniqueness

        d = dict(src_dict)
        column_count = d.pop("column_count")

        completeness = QualityReportOutCompleteness.from_dict(d.pop("completeness"))

        consistency = QualityReportOutConsistency.from_dict(d.pop("consistency"))

        overall_score = d.pop("overall_score")

        row_count = d.pop("row_count")

        uniqueness = QualityReportOutUniqueness.from_dict(d.pop("uniqueness"))

        recommendations = cast(list[str], d.pop("recommendations", UNSET))

        quality_report_out = cls(
            column_count=column_count,
            completeness=completeness,
            consistency=consistency,
            overall_score=overall_score,
            row_count=row_count,
            uniqueness=uniqueness,
            recommendations=recommendations,
        )

        quality_report_out.additional_properties = d
        return quality_report_out

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
