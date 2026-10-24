from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.decision_table_in_mode import DecisionTableInMode
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decision_table_row_in import DecisionTableRowIn


T = TypeVar("T", bound="DecisionTableIn")


@_attrs_define
class DecisionTableIn:
    """
    Attributes:
        rows (list[DecisionTableRowIn]): The table rows (2-50).
        mode (DecisionTableInMode | Unset): 'ladder' (>= 2 rows, one default, distinct orders) or 'partition' (mutually
            exclusive cells: no default/order/permits). Default: DecisionTableInMode.LADDER.
    """

    rows: list[DecisionTableRowIn]
    mode: DecisionTableInMode | Unset = DecisionTableInMode.LADDER
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rows = []
        for rows_item_data in self.rows:
            rows_item = rows_item_data.to_dict()
            rows.append(rows_item)

        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "rows": rows,
            }
        )
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.decision_table_row_in import DecisionTableRowIn

        d = dict(src_dict)
        rows = []
        _rows = d.pop("rows")
        for rows_item_data in _rows:
            rows_item = DecisionTableRowIn.from_dict(rows_item_data)

            rows.append(rows_item)

        _mode = d.pop("mode", UNSET)
        mode: DecisionTableInMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = DecisionTableInMode(_mode)

        decision_table_in = cls(
            rows=rows,
            mode=mode,
        )

        decision_table_in.additional_properties = d
        return decision_table_in

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
