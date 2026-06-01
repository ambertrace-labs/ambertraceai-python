from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_preview_columns_item import DatasetPreviewColumnsItem
    from ..models.dataset_preview_rows_item import DatasetPreviewRowsItem


T = TypeVar("T", bound="DatasetPreview")


@_attrs_define
class DatasetPreview:
    """
    Attributes:
        columns (list[DatasetPreviewColumnsItem] | Unset):
        rows (list[DatasetPreviewRowsItem] | Unset):
        total_rows (int | Unset):  Default: 0.
    """

    columns: list[DatasetPreviewColumnsItem] | Unset = UNSET
    rows: list[DatasetPreviewRowsItem] | Unset = UNSET
    total_rows: int | Unset = 0
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        columns: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.columns, Unset):
            columns = []
            for columns_item_data in self.columns:
                columns_item = columns_item_data.to_dict()
                columns.append(columns_item)

        rows: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.rows, Unset):
            rows = []
            for rows_item_data in self.rows:
                rows_item = rows_item_data.to_dict()
                rows.append(rows_item)

        total_rows = self.total_rows

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if columns is not UNSET:
            field_dict["columns"] = columns
        if rows is not UNSET:
            field_dict["rows"] = rows
        if total_rows is not UNSET:
            field_dict["total_rows"] = total_rows

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_preview_columns_item import DatasetPreviewColumnsItem
        from ..models.dataset_preview_rows_item import DatasetPreviewRowsItem

        d = dict(src_dict)
        _columns = d.pop("columns", UNSET)
        columns: list[DatasetPreviewColumnsItem] | Unset = UNSET
        if _columns is not UNSET:
            columns = []
            for columns_item_data in _columns:
                columns_item = DatasetPreviewColumnsItem.from_dict(columns_item_data)

                columns.append(columns_item)

        _rows = d.pop("rows", UNSET)
        rows: list[DatasetPreviewRowsItem] | Unset = UNSET
        if _rows is not UNSET:
            rows = []
            for rows_item_data in _rows:
                rows_item = DatasetPreviewRowsItem.from_dict(rows_item_data)

                rows.append(rows_item)

        total_rows = d.pop("total_rows", UNSET)

        dataset_preview = cls(
            columns=columns,
            rows=rows,
            total_rows=total_rows,
        )

        dataset_preview.additional_properties = d
        return dataset_preview

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
