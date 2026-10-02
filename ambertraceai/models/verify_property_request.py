from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.verify_property_space import VerifyPropertySpace


T = TypeVar("T", bound="VerifyPropertyRequest")


@_attrs_define
class VerifyPropertyRequest:
    """
    Attributes:
        property_ (str): The universal property to certify. v1: 'strategy_proof'.
        space (VerifyPropertySpace): The finite space a ``verify_property`` claim quantifies over (v1 grammar).

            The space is the PRODUCT of every agent's type domain x which agent deviates x
            that agent's misreport domain; ``|S|`` is recomputed by the proven checker.
    """

    property_: str
    space: VerifyPropertySpace
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        space = self.space.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "property": property_,
                "space": space,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_property_space import VerifyPropertySpace

        d = dict(src_dict)
        property_ = d.pop("property")

        space = VerifyPropertySpace.from_dict(d.pop("space"))

        verify_property_request = cls(
            property_=property_,
            space=space,
        )

        verify_property_request.additional_properties = d
        return verify_property_request

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
