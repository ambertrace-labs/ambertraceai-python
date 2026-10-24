from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decision_table_out_rows_item import DecisionTableOutRowsItem


T = TypeVar("T", bound="DecisionTableOut")


@_attrs_define
class DecisionTableOut:
    """
    Attributes:
        applied (str):
        mode (str):
        provenance (str):
        rows (list[DecisionTableOutRowsItem]):
        guessed (list[str] | None | Unset): Row fields an inference step filled by convention rather than read
            ('default', 'order', 'permits'); absent on a declared table.
    """

    applied: str
    mode: str
    provenance: str
    rows: list[DecisionTableOutRowsItem]
    guessed: list[str] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        applied = self.applied

        mode = self.mode

        provenance = self.provenance

        rows = []
        for rows_item_data in self.rows:
            rows_item = rows_item_data.to_dict()
            rows.append(rows_item)

        guessed: list[str] | None | Unset
        if isinstance(self.guessed, Unset):
            guessed = UNSET
        elif isinstance(self.guessed, list):
            guessed = self.guessed

        else:
            guessed = self.guessed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "applied": applied,
                "mode": mode,
                "provenance": provenance,
                "rows": rows,
            }
        )
        if guessed is not UNSET:
            field_dict["guessed"] = guessed

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.decision_table_out_rows_item import DecisionTableOutRowsItem

        d = dict(src_dict)
        applied = d.pop("applied")

        mode = d.pop("mode")

        provenance = d.pop("provenance")

        rows = []
        _rows = d.pop("rows")
        for rows_item_data in _rows:
            rows_item = DecisionTableOutRowsItem.from_dict(rows_item_data)

            rows.append(rows_item)

        def _parse_guessed(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                guessed_type_0 = cast(list[str], data)

                return guessed_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        guessed = _parse_guessed(d.pop("guessed", UNSET))

        decision_table_out = cls(
            applied=applied,
            mode=mode,
            provenance=provenance,
            rows=rows,
            guessed=guessed,
        )

        decision_table_out.additional_properties = d
        return decision_table_out

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
