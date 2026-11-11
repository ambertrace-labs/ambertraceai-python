from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="VerifyPropertyPayoffExpr")


@_attrs_define
class VerifyPropertyPayoffExpr:
    """A payoff cell computed from a named integer parameter: ``param * mul + add``.

    Attributes:
        param (str): Name of an entry in `game.parameters`.
        add (int | Unset): Integer offset (default 0). Default: 0.
        mul (int | Unset): Integer multiplier (default 1). Default: 1.
    """

    param: str
    add: int | Unset = 0
    mul: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        param = self.param

        add = self.add

        mul = self.mul

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "param": param,
            }
        )
        if add is not UNSET:
            field_dict["add"] = add
        if mul is not UNSET:
            field_dict["mul"] = mul

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        param = d.pop("param")

        add = d.pop("add", UNSET)

        mul = d.pop("mul", UNSET)

        verify_property_payoff_expr = cls(
            param=param,
            add=add,
            mul=mul,
        )

        verify_property_payoff_expr.additional_properties = d
        return verify_property_payoff_expr

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
