from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.verify_property_game_parameters_type_0 import VerifyPropertyGameParametersType0
    from ..models.verify_property_payoff_row import VerifyPropertyPayoffRow


T = TypeVar("T", bound="VerifyPropertyGame")


@_attrs_define
class VerifyPropertyGame:
    """A custom finite normal-form game (the `space` of the game-theoretic properties).

    Attributes:
        payoffs (list[VerifyPropertyPayoffRow]): The explicit payoff table: EXACTLY one row per action profile (a
            missing or duplicated profile is an ABSTAIN, never a guess).
        players (list[list[str]]): Per player (in order), its finite action set: distinct alphanumeric names. At most 8
            actions each. Asymmetric games: 2-6 players, at most 1024 profiles. Symmetric games (every player has the
            identical action set and the table is symmetric): up to 30 players and 131072 profiles.
        parameters (None | Unset | VerifyPropertyGameParametersType0): Optional named values referenced by payoff cells.
            A plain integer is taken as you typed it (NO provenance claim). A CertifiedOutputRef is resolved by the server
            from a certified output in your organisation (fail-closed: an unknown, other-organisation, uncertified or
            pending source is an ABSTAIN with a named reason) and listed in the verdict's `inherited_provenance`. The
            resolved table is echoed back as `resolved_payoffs`.
    """

    payoffs: list[VerifyPropertyPayoffRow]
    players: list[list[str]]
    parameters: None | Unset | VerifyPropertyGameParametersType0 = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.verify_property_game_parameters_type_0 import VerifyPropertyGameParametersType0

        payoffs = []
        for payoffs_item_data in self.payoffs:
            payoffs_item = payoffs_item_data.to_dict()
            payoffs.append(payoffs_item)

        players = []
        for players_item_data in self.players:
            players_item = players_item_data

            players.append(players_item)

        parameters: dict[str, Any] | None | Unset
        if isinstance(self.parameters, Unset):
            parameters = UNSET
        elif isinstance(self.parameters, VerifyPropertyGameParametersType0):
            parameters = self.parameters.to_dict()
        else:
            parameters = self.parameters

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "payoffs": payoffs,
                "players": players,
            }
        )
        if parameters is not UNSET:
            field_dict["parameters"] = parameters

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_property_game_parameters_type_0 import VerifyPropertyGameParametersType0
        from ..models.verify_property_payoff_row import VerifyPropertyPayoffRow

        d = dict(src_dict)
        payoffs = []
        _payoffs = d.pop("payoffs")
        for payoffs_item_data in _payoffs:
            payoffs_item = VerifyPropertyPayoffRow.from_dict(payoffs_item_data)

            payoffs.append(payoffs_item)

        players = []
        _players = d.pop("players")
        for players_item_data in _players:
            players_item = cast(list[str], players_item_data)

            players.append(players_item)

        def _parse_parameters(data: object) -> None | Unset | VerifyPropertyGameParametersType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                parameters_type_0 = VerifyPropertyGameParametersType0.from_dict(data)

                return parameters_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VerifyPropertyGameParametersType0, data)

        parameters = _parse_parameters(d.pop("parameters", UNSET))

        verify_property_game = cls(
            payoffs=payoffs,
            players=players,
            parameters=parameters,
        )

        verify_property_game.additional_properties = d
        return verify_property_game

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
