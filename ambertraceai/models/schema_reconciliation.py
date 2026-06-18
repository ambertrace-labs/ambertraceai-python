from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.schema_reconciliation_augment import SchemaReconciliationAugment
    from ..models.schema_reconciliation_conflict import SchemaReconciliationConflict


T = TypeVar("T", bound="SchemaReconciliation")


@_attrs_define
class SchemaReconciliation:
    """Column-mapping report for a rule create/edit (data-driven ontology §2.3).

    ``status`` is ``ok`` when every input-field reference bound to a real column
    or an in-set derived head, or ``conflict`` when at least one reference could
    not be mapped (the edit is rejected with HTTP 400 in that case and this
    report is returned alongside the error under the top-level
    ``schema_reconciliation`` key).

        Attributes:
            status (str): 'ok' or 'conflict'.
            augmented (list[SchemaReconciliationAugment] | Unset): References that were remapped to a real column.
            conflicts (list[SchemaReconciliationConflict] | Unset): References that could not be mapped (present on a
                conflict).
    """

    status: str
    augmented: list[SchemaReconciliationAugment] | Unset = UNSET
    conflicts: list[SchemaReconciliationConflict] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        status = self.status

        augmented: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.augmented, Unset):
            augmented = []
            for augmented_item_data in self.augmented:
                augmented_item = augmented_item_data.to_dict()
                augmented.append(augmented_item)

        conflicts: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.conflicts, Unset):
            conflicts = []
            for conflicts_item_data in self.conflicts:
                conflicts_item = conflicts_item_data.to_dict()
                conflicts.append(conflicts_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "status": status,
            }
        )
        if augmented is not UNSET:
            field_dict["augmented"] = augmented
        if conflicts is not UNSET:
            field_dict["conflicts"] = conflicts

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.schema_reconciliation_augment import SchemaReconciliationAugment
        from ..models.schema_reconciliation_conflict import SchemaReconciliationConflict

        d = dict(src_dict)
        status = d.pop("status")

        _augmented = d.pop("augmented", UNSET)
        augmented: list[SchemaReconciliationAugment] | Unset = UNSET
        if _augmented is not UNSET:
            augmented = []
            for augmented_item_data in _augmented:
                augmented_item = SchemaReconciliationAugment.from_dict(
                    augmented_item_data
                )

                augmented.append(augmented_item)

        _conflicts = d.pop("conflicts", UNSET)
        conflicts: list[SchemaReconciliationConflict] | Unset = UNSET
        if _conflicts is not UNSET:
            conflicts = []
            for conflicts_item_data in _conflicts:
                conflicts_item = SchemaReconciliationConflict.from_dict(
                    conflicts_item_data
                )

                conflicts.append(conflicts_item)

        schema_reconciliation = cls(
            status=status,
            augmented=augmented,
            conflicts=conflicts,
        )

        schema_reconciliation.additional_properties = d
        return schema_reconciliation

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
