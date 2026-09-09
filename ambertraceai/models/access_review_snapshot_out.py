from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.access_review_member_out import AccessReviewMemberOut
    from ..models.pagination_out import PaginationOut


T = TypeVar("T", bound="AccessReviewSnapshotOut")


@_attrs_define
class AccessReviewSnapshotOut:
    """Paginated access-review snapshot (SOC 2 CC6.2/6.3).

    Attributes:
        data (list[AccessReviewMemberOut]):
        generated_at (str):
        pagination (PaginationOut): Pagination metadata for paginated list responses.
    """

    data: list[AccessReviewMemberOut]
    generated_at: str
    pagination: PaginationOut
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = []
        for data_item_data in self.data:
            data_item = data_item_data.to_dict()
            data.append(data_item)

        generated_at = self.generated_at

        pagination = self.pagination.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data": data,
                "generated_at": generated_at,
                "pagination": pagination,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.access_review_member_out import AccessReviewMemberOut
        from ..models.pagination_out import PaginationOut

        d = dict(src_dict)
        data = []
        _data = d.pop("data")
        for data_item_data in _data:
            data_item = AccessReviewMemberOut.from_dict(data_item_data)

            data.append(data_item)

        generated_at = d.pop("generated_at")

        pagination = PaginationOut.from_dict(d.pop("pagination"))

        access_review_snapshot_out = cls(
            data=data,
            generated_at=generated_at,
            pagination=pagination,
        )

        access_review_snapshot_out.additional_properties = d
        return access_review_snapshot_out

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
