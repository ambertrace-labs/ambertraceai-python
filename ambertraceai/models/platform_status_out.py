from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.platform_status_out_decision_table_type_0 import PlatformStatusOutDecisionTableType0
    from ..models.platform_status_out_decision_table_warnings_item import PlatformStatusOutDecisionTableWarningsItem


T = TypeVar("T", bound="PlatformStatusOut")


@_attrs_define
class PlatformStatusOut:
    """
    Attributes:
        name (str):
        platform_id (int):
        status (str):
        decision_table (None | PlatformStatusOutDecisionTableType0 | Unset): The Decision Table the platform was built
            with {mode, rows: [{id, label, order, default, permits, values}], provenance, applied}; provenance 'backfill'
            marks a table derived for a platform built before tables existed. Null when none is declared.
        decision_table_note (None | str | Unset): 'no decisions declared' when the platform has no decision table (it
            builds as a Q&A platform); null otherwise.
        decision_table_warnings (list[PlatformStatusOutDecisionTableWarningsItem] | Unset): Advisory consistency
            findings (C1, C3, C4, C6; C4 first) recorded when the platform was built; each names the value / sentence /
            field / row.
        version (int | Unset):  Default: 1.
    """

    name: str
    platform_id: int
    status: str
    decision_table: None | PlatformStatusOutDecisionTableType0 | Unset = UNSET
    decision_table_note: None | str | Unset = UNSET
    decision_table_warnings: list[PlatformStatusOutDecisionTableWarningsItem] | Unset = UNSET
    version: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.platform_status_out_decision_table_type_0 import PlatformStatusOutDecisionTableType0

        name = self.name

        platform_id = self.platform_id

        status = self.status

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, PlatformStatusOutDecisionTableType0):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        decision_table_note: None | str | Unset
        if isinstance(self.decision_table_note, Unset):
            decision_table_note = UNSET
        else:
            decision_table_note = self.decision_table_note

        decision_table_warnings: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.decision_table_warnings, Unset):
            decision_table_warnings = []
            for decision_table_warnings_item_data in self.decision_table_warnings:
                decision_table_warnings_item = decision_table_warnings_item_data.to_dict()
                decision_table_warnings.append(decision_table_warnings_item)

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "platform_id": platform_id,
                "status": status,
            }
        )
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table
        if decision_table_note is not UNSET:
            field_dict["decision_table_note"] = decision_table_note
        if decision_table_warnings is not UNSET:
            field_dict["decision_table_warnings"] = decision_table_warnings
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_status_out_decision_table_type_0 import PlatformStatusOutDecisionTableType0
        from ..models.platform_status_out_decision_table_warnings_item import PlatformStatusOutDecisionTableWarningsItem

        d = dict(src_dict)
        name = d.pop("name")

        platform_id = d.pop("platform_id")

        status = d.pop("status")

        def _parse_decision_table(data: object) -> None | PlatformStatusOutDecisionTableType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_table_type_0 = PlatformStatusOutDecisionTableType0.from_dict(data)

                return decision_table_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlatformStatusOutDecisionTableType0 | Unset, data)

        decision_table = _parse_decision_table(d.pop("decision_table", UNSET))

        def _parse_decision_table_note(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decision_table_note = _parse_decision_table_note(d.pop("decision_table_note", UNSET))

        _decision_table_warnings = d.pop("decision_table_warnings", UNSET)
        decision_table_warnings: list[PlatformStatusOutDecisionTableWarningsItem] | Unset = UNSET
        if _decision_table_warnings is not UNSET:
            decision_table_warnings = []
            for decision_table_warnings_item_data in _decision_table_warnings:
                decision_table_warnings_item = PlatformStatusOutDecisionTableWarningsItem.from_dict(
                    decision_table_warnings_item_data
                )

                decision_table_warnings.append(decision_table_warnings_item)

        version = d.pop("version", UNSET)

        platform_status_out = cls(
            name=name,
            platform_id=platform_id,
            status=status,
            decision_table=decision_table,
            decision_table_note=decision_table_note,
            decision_table_warnings=decision_table_warnings,
            version=version,
        )

        platform_status_out.additional_properties = d
        return platform_status_out

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
