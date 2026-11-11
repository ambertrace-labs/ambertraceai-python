from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.verify_property_payoff_expr import VerifyPropertyPayoffExpr


T = TypeVar("T", bound="VerifyPropertyPayoffRow")


@_attrs_define
class VerifyPropertyPayoffRow:
    """One payoff-table row: a full action profile and every player's payoff.

    Attributes:
        actions (list[str]): One action per player, in player order (each from that player's set).
        utilities (list[int | VerifyPropertyPayoffExpr]): One integer payoff per player, in player order; a cell may
            instead be {param, mul, add} resolved from `game.parameters`.
    """

    actions: list[str]
    utilities: list[int | VerifyPropertyPayoffExpr]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.verify_property_payoff_expr import VerifyPropertyPayoffExpr

        actions = self.actions

        utilities = []
        for utilities_item_data in self.utilities:
            utilities_item: dict[str, Any] | int
            if isinstance(utilities_item_data, VerifyPropertyPayoffExpr):
                utilities_item = utilities_item_data.to_dict()
            else:
                utilities_item = utilities_item_data
            utilities.append(utilities_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "actions": actions,
                "utilities": utilities,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_property_payoff_expr import VerifyPropertyPayoffExpr

        d = dict(src_dict)
        actions = cast(list[str], d.pop("actions"))

        utilities = []
        _utilities = d.pop("utilities")
        for utilities_item_data in _utilities:

            def _parse_utilities_item(data: object) -> int | VerifyPropertyPayoffExpr:
                try:
                    if not isinstance(data, dict):
                        raise TypeError()
                    utilities_item_type_1 = VerifyPropertyPayoffExpr.from_dict(data)

                    return utilities_item_type_1
                except (TypeError, ValueError, AttributeError, KeyError):
                    pass
                return cast(int | VerifyPropertyPayoffExpr, data)

            utilities_item = _parse_utilities_item(utilities_item_data)

            utilities.append(utilities_item)

        verify_property_payoff_row = cls(
            actions=actions,
            utilities=utilities,
        )

        verify_property_payoff_row.additional_properties = d
        return verify_property_payoff_row

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
