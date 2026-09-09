from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.dataset_derive_request_op import DatasetDeriveRequestOp
from ..types import UNSET, Unset

T = TypeVar("T", bound="DatasetDeriveRequest")


@_attrs_define
class DatasetDeriveRequest:
    """Derive one new column as a fixed binary arithmetic expression.

    v1 grammar (deliberately minimal): exactly ONE op over TWO
    EXISTING named columns -> ONE new named column. No scalars, no chaining,
    no general expression evaluator.

        Attributes:
            left (str): Existing column name (LHS).
            new_column (str): Name of the new column to create. 409 if it already exists.
            op (DatasetDeriveRequestOp): Binary arithmetic operator. subtract=left-right, add=left+right,
                multiply=left*right, divide=left/right (division by zero -> NaN, never inf).
            right (str): Existing column name (RHS).
            drop_source_columns (bool | Unset): Drop left+right from the dataset AFTER computing the derived column (default
                true). Recommended when the derived column is a forecast target: leaving the two legs in the panel makes them
                mechanically-perfect drivers of their own derivation (the slope IS a linear function of the legs), which defeats
                driver discovery on the derived target. The time/join index column is never dropped even if named as an operand.
                Default: True.
    """

    left: str
    new_column: str
    op: DatasetDeriveRequestOp
    right: str
    drop_source_columns: bool | Unset = True
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        left = self.left

        new_column = self.new_column

        op = self.op.value

        right = self.right

        drop_source_columns = self.drop_source_columns

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "left": left,
                "new_column": new_column,
                "op": op,
                "right": right,
            }
        )
        if drop_source_columns is not UNSET:
            field_dict["drop_source_columns"] = drop_source_columns

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        left = d.pop("left")

        new_column = d.pop("new_column")

        op = DatasetDeriveRequestOp(d.pop("op"))

        right = d.pop("right")

        drop_source_columns = d.pop("drop_source_columns", UNSET)

        dataset_derive_request = cls(
            left=left,
            new_column=new_column,
            op=op,
            right=right,
            drop_source_columns=drop_source_columns,
        )

        dataset_derive_request.additional_properties = d
        return dataset_derive_request

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
