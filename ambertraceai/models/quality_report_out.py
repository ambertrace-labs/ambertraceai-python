from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.quality_report_out_completeness import QualityReportOutCompleteness
    from ..models.quality_report_out_consistency import QualityReportOutConsistency
    from ..models.quality_report_out_decision_table_type_0 import QualityReportOutDecisionTableType0
    from ..models.quality_report_out_uniqueness import QualityReportOutUniqueness
    from ..models.quality_report_out_warnings_item import QualityReportOutWarningsItem


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
        decision_table (None | QualityReportOutDecisionTableType0 | Unset): Decision Table section (focal datasets):
            label_column {name, source: declared|proposed}, table (the stored table with provenance / applied / guessed),
            proposal (the table the label column would seed), description_scaffold (text drawn from the schema), checks
            {blocking, warnings} (C4 first; each item names the value / sentence / field), note ('no decisions declared'
            when there is no table).
        recommendations (list[str] | Unset):
        warnings (list[QualityReportOutWarningsItem] | Unset):
    """

    column_count: int
    completeness: QualityReportOutCompleteness
    consistency: QualityReportOutConsistency
    overall_score: float
    row_count: int
    uniqueness: QualityReportOutUniqueness
    decision_table: None | QualityReportOutDecisionTableType0 | Unset = UNSET
    recommendations: list[str] | Unset = UNSET
    warnings: list[QualityReportOutWarningsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.quality_report_out_decision_table_type_0 import QualityReportOutDecisionTableType0

        column_count = self.column_count

        completeness = self.completeness.to_dict()

        consistency = self.consistency.to_dict()

        overall_score = self.overall_score

        row_count = self.row_count

        uniqueness = self.uniqueness.to_dict()

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, QualityReportOutDecisionTableType0):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        recommendations: list[str] | Unset = UNSET
        if not isinstance(self.recommendations, Unset):
            recommendations = self.recommendations

        warnings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.warnings, Unset):
            warnings = []
            for warnings_item_data in self.warnings:
                warnings_item = warnings_item_data.to_dict()
                warnings.append(warnings_item)

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
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table
        if recommendations is not UNSET:
            field_dict["recommendations"] = recommendations
        if warnings is not UNSET:
            field_dict["warnings"] = warnings

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.quality_report_out_completeness import QualityReportOutCompleteness
        from ..models.quality_report_out_consistency import QualityReportOutConsistency
        from ..models.quality_report_out_decision_table_type_0 import QualityReportOutDecisionTableType0
        from ..models.quality_report_out_uniqueness import QualityReportOutUniqueness
        from ..models.quality_report_out_warnings_item import QualityReportOutWarningsItem

        d = dict(src_dict)
        column_count = d.pop("column_count")

        completeness = QualityReportOutCompleteness.from_dict(d.pop("completeness"))

        consistency = QualityReportOutConsistency.from_dict(d.pop("consistency"))

        overall_score = d.pop("overall_score")

        row_count = d.pop("row_count")

        uniqueness = QualityReportOutUniqueness.from_dict(d.pop("uniqueness"))

        def _parse_decision_table(data: object) -> None | QualityReportOutDecisionTableType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_table_type_0 = QualityReportOutDecisionTableType0.from_dict(data)

                return decision_table_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | QualityReportOutDecisionTableType0 | Unset, data)

        decision_table = _parse_decision_table(d.pop("decision_table", UNSET))

        recommendations = cast(list[str], d.pop("recommendations", UNSET))

        _warnings = d.pop("warnings", UNSET)
        warnings: list[QualityReportOutWarningsItem] | Unset = UNSET
        if _warnings is not UNSET:
            warnings = []
            for warnings_item_data in _warnings:
                warnings_item = QualityReportOutWarningsItem.from_dict(warnings_item_data)

                warnings.append(warnings_item)

        quality_report_out = cls(
            column_count=column_count,
            completeness=completeness,
            consistency=consistency,
            overall_score=overall_score,
            row_count=row_count,
            uniqueness=uniqueness,
            decision_table=decision_table,
            recommendations=recommendations,
            warnings=warnings,
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
