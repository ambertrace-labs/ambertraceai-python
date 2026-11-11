from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.verify_property_game import VerifyPropertyGame
    from ..models.verify_property_variable import VerifyPropertyVariable


T = TypeVar("T", bound="VerifyPropertySpace")


@_attrs_define
class VerifyPropertySpace:
    """The finite space a ``verify_property`` claim quantifies over.

    ``strategy_proof``: the PRODUCT of every agent's type domain x which agent deviates x
    that agent's misreport domain (`mechanism`, `agents`, `domain`).
    ``exactly_one_verdict``: the PRODUCT of the declared `variables` domains (the regime
    grid) over the platform's own active decision rules.  ``|S|`` is recomputed by the
    proven checker.

        Attributes:
            bound (int): REQUIRED finiteness bound: the largest |S| you accept. A space larger than `bound` (or than the
                platform ceiling) is an explicit ABSTAIN, never a partial answer.
            action (None | str | Unset): dominant_strategy / best_response: the claimed action of `player`.
            agents (int | None | Unset): strategy_proof only. Number of agents (voters / bidders); the v1 library supports 1
                to 8.
            domain (list[int | str] | None | Unset): strategy_proof only. The finite value domain. plurality / majority: the
                alternatives (alphanumeric names, e.g. ['A','B','C']); vickrey / first_price: the discrete bid grid (distinct
                non-negative integers, at most 10). At most 64 entries are accepted at all (the library's own caps are tighter).
            game (None | Unset | VerifyPropertyGame): Custom-game properties only (nash_equilibrium, dominant_strategy,
                best_response, pareto_optimal, pareto_dominated): the normal-form game. The space is searched exhaustively over
                what the claim quantifies (opponent profiles x deviations; or every profile for Pareto); beyond `bound` / the
                platform ceiling the answer is an explicit ABSTAIN.
            mechanism (None | str | Unset): strategy_proof only. Mechanism library entry: 'plurality' (3-5 alternatives,
                ties break in `domain` order), 'majority' (exactly 2 alternatives, tie -> first), 'vickrey' (2 bidders, second-
                price) or 'first_price' (2 bidders, first-price; a manipulable control).
            opponent_profile (list[str] | None | Unset): best_response: the other players' actions, in player order
                (`player` omitted).
            player (int | None | Unset): dominant_strategy / best_response: the 1-based player.
            profile (list[str] | None | Unset): nash_equilibrium / pareto_optimal / pareto_dominated: the action profile
                (one action per player) the claim is about.
            require_totality (bool | Unset): exactly_one_verdict only. True (default): every cell must derive EXACTLY ONE
                verdict (totality + exclusivity). False: AT-MOST-ONE -- a cell deriving no verdict is allowed, only two co-
                firing verdicts is a violation. Default: True.
            strict (bool | Unset): dominant_strategy only. False (default): weakly dominant (never worse than any
                alternative against any opponent profile). True: strictly better than every alternative against every opponent
                profile. Default: False.
            variables (list[VerifyPropertyVariable] | None | Unset): exactly_one_verdict only. The regime grid: each axis is
                a rule-condition field with its explicit finite domain, e.g. [{'field': 'priced', 'domain':
                ['neg','zero','pos']}, {'field': 'reaction', 'domain': ['hawk','dove']}]. Every cell of the product is checked
                to derive EXACTLY ONE verdict from the platform's active decision rules; a rule leaf that is not a scalar test
                on a declared field makes the query ABSTAIN (condition_out_of_fragment / field_outside_grid).
    """

    bound: int
    action: None | str | Unset = UNSET
    agents: int | None | Unset = UNSET
    domain: list[int | str] | None | Unset = UNSET
    game: None | Unset | VerifyPropertyGame = UNSET
    mechanism: None | str | Unset = UNSET
    opponent_profile: list[str] | None | Unset = UNSET
    player: int | None | Unset = UNSET
    profile: list[str] | None | Unset = UNSET
    require_totality: bool | Unset = True
    strict: bool | Unset = False
    variables: list[VerifyPropertyVariable] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.verify_property_game import VerifyPropertyGame

        bound = self.bound

        action: None | str | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        else:
            action = self.action

        agents: int | None | Unset
        if isinstance(self.agents, Unset):
            agents = UNSET
        else:
            agents = self.agents

        domain: list[int | str] | None | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        elif isinstance(self.domain, list):
            domain = []
            for domain_type_0_item_data in self.domain:
                domain_type_0_item: int | str
                domain_type_0_item = domain_type_0_item_data
                domain.append(domain_type_0_item)

        else:
            domain = self.domain

        game: dict[str, Any] | None | Unset
        if isinstance(self.game, Unset):
            game = UNSET
        elif isinstance(self.game, VerifyPropertyGame):
            game = self.game.to_dict()
        else:
            game = self.game

        mechanism: None | str | Unset
        if isinstance(self.mechanism, Unset):
            mechanism = UNSET
        else:
            mechanism = self.mechanism

        opponent_profile: list[str] | None | Unset
        if isinstance(self.opponent_profile, Unset):
            opponent_profile = UNSET
        elif isinstance(self.opponent_profile, list):
            opponent_profile = self.opponent_profile

        else:
            opponent_profile = self.opponent_profile

        player: int | None | Unset
        if isinstance(self.player, Unset):
            player = UNSET
        else:
            player = self.player

        profile: list[str] | None | Unset
        if isinstance(self.profile, Unset):
            profile = UNSET
        elif isinstance(self.profile, list):
            profile = self.profile

        else:
            profile = self.profile

        require_totality = self.require_totality

        strict = self.strict

        variables: list[dict[str, Any]] | None | Unset
        if isinstance(self.variables, Unset):
            variables = UNSET
        elif isinstance(self.variables, list):
            variables = []
            for variables_type_0_item_data in self.variables:
                variables_type_0_item = variables_type_0_item_data.to_dict()
                variables.append(variables_type_0_item)

        else:
            variables = self.variables

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "bound": bound,
            }
        )
        if action is not UNSET:
            field_dict["action"] = action
        if agents is not UNSET:
            field_dict["agents"] = agents
        if domain is not UNSET:
            field_dict["domain"] = domain
        if game is not UNSET:
            field_dict["game"] = game
        if mechanism is not UNSET:
            field_dict["mechanism"] = mechanism
        if opponent_profile is not UNSET:
            field_dict["opponent_profile"] = opponent_profile
        if player is not UNSET:
            field_dict["player"] = player
        if profile is not UNSET:
            field_dict["profile"] = profile
        if require_totality is not UNSET:
            field_dict["require_totality"] = require_totality
        if strict is not UNSET:
            field_dict["strict"] = strict
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_property_game import VerifyPropertyGame
        from ..models.verify_property_variable import VerifyPropertyVariable

        d = dict(src_dict)
        bound = d.pop("bound")

        def _parse_action(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        def _parse_agents(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        agents = _parse_agents(d.pop("agents", UNSET))

        def _parse_domain(data: object) -> list[int | str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                domain_type_0 = []
                _domain_type_0 = data
                for domain_type_0_item_data in _domain_type_0:

                    def _parse_domain_type_0_item(data: object) -> int | str:
                        return cast(int | str, data)

                    domain_type_0_item = _parse_domain_type_0_item(domain_type_0_item_data)

                    domain_type_0.append(domain_type_0_item)

                return domain_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int | str] | None | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_game(data: object) -> None | Unset | VerifyPropertyGame:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                game_type_0 = VerifyPropertyGame.from_dict(data)

                return game_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VerifyPropertyGame, data)

        game = _parse_game(d.pop("game", UNSET))

        def _parse_mechanism(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        mechanism = _parse_mechanism(d.pop("mechanism", UNSET))

        def _parse_opponent_profile(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                opponent_profile_type_0 = cast(list[str], data)

                return opponent_profile_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        opponent_profile = _parse_opponent_profile(d.pop("opponent_profile", UNSET))

        def _parse_player(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        player = _parse_player(d.pop("player", UNSET))

        def _parse_profile(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                profile_type_0 = cast(list[str], data)

                return profile_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        profile = _parse_profile(d.pop("profile", UNSET))

        require_totality = d.pop("require_totality", UNSET)

        strict = d.pop("strict", UNSET)

        def _parse_variables(data: object) -> list[VerifyPropertyVariable] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                variables_type_0 = []
                _variables_type_0 = data
                for variables_type_0_item_data in _variables_type_0:
                    variables_type_0_item = VerifyPropertyVariable.from_dict(variables_type_0_item_data)

                    variables_type_0.append(variables_type_0_item)

                return variables_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[VerifyPropertyVariable] | None | Unset, data)

        variables = _parse_variables(d.pop("variables", UNSET))

        verify_property_space = cls(
            bound=bound,
            action=action,
            agents=agents,
            domain=domain,
            game=game,
            mechanism=mechanism,
            opponent_profile=opponent_profile,
            player=player,
            profile=profile,
            require_totality=require_totality,
            strict=strict,
            variables=variables,
        )

        verify_property_space.additional_properties = d
        return verify_property_space

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
