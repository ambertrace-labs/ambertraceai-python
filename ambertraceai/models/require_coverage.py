from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.require_coverage_relative_to import RequireCoverageRelativeTo
from ..types import UNSET, Unset

T = TypeVar("T", bound="RequireCoverage")


@_attrs_define
class RequireCoverage:
    """Coverage filter for multi-source panels.

    Applied on the RAW (pre-fill) outer-joined frame, AFTER on_stale and
    BEFORE on_missing: drops AUXILIARY columns whose non-null coverage falls
    below ``min_pct``. CORE columns are NEVER dropped by this filter -- a low-
    coverage core column is not this policy's problem to solve (declare it
    auxiliary, or use on_stale for a discontinued core column).

        Attributes:
            min_pct (float): Minimum non-null coverage percentage for an AUXILIARY column to survive. Columns at or above
                this threshold are kept; columns below it are dropped and recorded in schema_info['coverage_filter_dropped'].
            relative_to (RequireCoverageRelativeTo | Unset): Denominator for the coverage percentage. 'panel' (default) --
                non-null count as a percentage of the total panel row count. 'core' -- non-null count as a percentage of the
                rows where EVERY core column is non-null (the core-column intersection), so a low-coverage core-adjacent
                auxiliary column is judged against the window that actually matters for training. Default:
                RequireCoverageRelativeTo.PANEL.
    """

    min_pct: float
    relative_to: RequireCoverageRelativeTo | Unset = RequireCoverageRelativeTo.PANEL
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        min_pct = self.min_pct

        relative_to: str | Unset = UNSET
        if not isinstance(self.relative_to, Unset):
            relative_to = self.relative_to.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "min_pct": min_pct,
            }
        )
        if relative_to is not UNSET:
            field_dict["relative_to"] = relative_to

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        min_pct = d.pop("min_pct")

        _relative_to = d.pop("relative_to", UNSET)
        relative_to: RequireCoverageRelativeTo | Unset
        if isinstance(_relative_to, Unset):
            relative_to = UNSET
        else:
            relative_to = RequireCoverageRelativeTo(_relative_to)

        require_coverage = cls(
            min_pct=min_pct,
            relative_to=relative_to,
        )

        require_coverage.additional_properties = d
        return require_coverage

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
