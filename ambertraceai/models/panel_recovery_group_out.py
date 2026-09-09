from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="PanelRecoveryGroupOut")


@_attrs_define
class PanelRecoveryGroupOut:
    """A set of columns that go missing TOGETHER.

    Reported because two series dying in the same window make every SINGLE
    column recovery zero -- a single-column-only report says "nothing is
    binding" on exactly that case.

        Attributes:
            columns (list[str]):
            rows_recovered_if_all_dropped (int):
            usable_rows_if_all_dropped (int):
            heuristic (str | Unset): Names the search that produced this group. 'observed_co_missing_sets': candidates are
                the co-missing sets actually OBSERVED as some row's exact missing set, not every subset of columns -- so the
                best set to drop may be a SUPERSET that never appears on its own. Enumerating all subsets is exponential in the
                column count; this is the deliberate trade. Candidates ARE scored by their true (subset) recovery and ranked
                before the list is truncated. Default: 'observed_co_missing_sets'.
    """

    columns: list[str]
    rows_recovered_if_all_dropped: int
    usable_rows_if_all_dropped: int
    heuristic: str | Unset = "observed_co_missing_sets"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        columns = self.columns

        rows_recovered_if_all_dropped = self.rows_recovered_if_all_dropped

        usable_rows_if_all_dropped = self.usable_rows_if_all_dropped

        heuristic = self.heuristic

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "columns": columns,
                "rows_recovered_if_all_dropped": rows_recovered_if_all_dropped,
                "usable_rows_if_all_dropped": usable_rows_if_all_dropped,
            }
        )
        if heuristic is not UNSET:
            field_dict["heuristic"] = heuristic

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        columns = cast(list[str], d.pop("columns"))

        rows_recovered_if_all_dropped = d.pop("rows_recovered_if_all_dropped")

        usable_rows_if_all_dropped = d.pop("usable_rows_if_all_dropped")

        heuristic = d.pop("heuristic", UNSET)

        panel_recovery_group_out = cls(
            columns=columns,
            rows_recovered_if_all_dropped=rows_recovered_if_all_dropped,
            usable_rows_if_all_dropped=usable_rows_if_all_dropped,
            heuristic=heuristic,
        )

        panel_recovery_group_out.additional_properties = d
        return panel_recovery_group_out

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
