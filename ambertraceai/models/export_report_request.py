from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ExportReportRequest")


@_attrs_define
class ExportReportRequest:
    """
    Attributes:
        query (str):
        format_ (str | Unset): Export format: pdf or json Default: 'pdf'.
        top_k (int | Unset):  Default: 10.
    """

    query: str
    format_: str | Unset = "pdf"
    top_k: int | Unset = 10
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        format_ = self.format_

        top_k = self.top_k

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
            }
        )
        if format_ is not UNSET:
            field_dict["format"] = format_
        if top_k is not UNSET:
            field_dict["top_k"] = top_k

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        query = d.pop("query")

        format_ = d.pop("format", UNSET)

        top_k = d.pop("top_k", UNSET)

        export_report_request = cls(
            query=query,
            format_=format_,
            top_k=top_k,
        )

        export_report_request.additional_properties = d
        return export_report_request

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
