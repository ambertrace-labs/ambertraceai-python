from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.suggestion_out_action_type_0 import SuggestionOutActionType0
    from ..models.suggestion_out_condition_type_0 import SuggestionOutConditionType0
    from ..models.suggestion_out_scorecard_type_0 import SuggestionOutScorecardType0


T = TypeVar("T", bound="SuggestionOut")


@_attrs_define
class SuggestionOut:
    """
    Attributes:
        id (int):
        name (str):
        platform_id (int):
        rule_type (str):
        action (None | SuggestionOutActionType0 | Unset):
        condition (None | SuggestionOutConditionType0 | Unset):
        description (None | str | Unset):
        is_active (bool | Unset):  Default: False.
        priority (int | Unset):  Default: 0.
        scorecard (None | SuggestionOutScorecardType0 | Unset):
        source (None | str | Unset):
    """

    id: int
    name: str
    platform_id: int
    rule_type: str
    action: None | SuggestionOutActionType0 | Unset = UNSET
    condition: None | SuggestionOutConditionType0 | Unset = UNSET
    description: None | str | Unset = UNSET
    is_active: bool | Unset = False
    priority: int | Unset = 0
    scorecard: None | SuggestionOutScorecardType0 | Unset = UNSET
    source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.suggestion_out_action_type_0 import SuggestionOutActionType0
        from ..models.suggestion_out_condition_type_0 import SuggestionOutConditionType0
        from ..models.suggestion_out_scorecard_type_0 import SuggestionOutScorecardType0

        id = self.id

        name = self.name

        platform_id = self.platform_id

        rule_type = self.rule_type

        action: dict[str, Any] | None | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        elif isinstance(self.action, SuggestionOutActionType0):
            action = self.action.to_dict()
        else:
            action = self.action

        condition: dict[str, Any] | None | Unset
        if isinstance(self.condition, Unset):
            condition = UNSET
        elif isinstance(self.condition, SuggestionOutConditionType0):
            condition = self.condition.to_dict()
        else:
            condition = self.condition

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_active = self.is_active

        priority = self.priority

        scorecard: dict[str, Any] | None | Unset
        if isinstance(self.scorecard, Unset):
            scorecard = UNSET
        elif isinstance(self.scorecard, SuggestionOutScorecardType0):
            scorecard = self.scorecard.to_dict()
        else:
            scorecard = self.scorecard

        source: None | str | Unset
        if isinstance(self.source, Unset):
            source = UNSET
        else:
            source = self.source

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "platform_id": platform_id,
                "rule_type": rule_type,
            }
        )
        if action is not UNSET:
            field_dict["action"] = action
        if condition is not UNSET:
            field_dict["condition"] = condition
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if priority is not UNSET:
            field_dict["priority"] = priority
        if scorecard is not UNSET:
            field_dict["scorecard"] = scorecard
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.suggestion_out_action_type_0 import SuggestionOutActionType0
        from ..models.suggestion_out_condition_type_0 import SuggestionOutConditionType0
        from ..models.suggestion_out_scorecard_type_0 import SuggestionOutScorecardType0

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        platform_id = d.pop("platform_id")

        rule_type = d.pop("rule_type")

        def _parse_action(data: object) -> None | SuggestionOutActionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                action_type_0 = SuggestionOutActionType0.from_dict(data)

                return action_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SuggestionOutActionType0 | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        def _parse_condition(
            data: object,
        ) -> None | SuggestionOutConditionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                condition_type_0 = SuggestionOutConditionType0.from_dict(data)

                return condition_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SuggestionOutConditionType0 | Unset, data)

        condition = _parse_condition(d.pop("condition", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        is_active = d.pop("is_active", UNSET)

        priority = d.pop("priority", UNSET)

        def _parse_scorecard(
            data: object,
        ) -> None | SuggestionOutScorecardType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scorecard_type_0 = SuggestionOutScorecardType0.from_dict(data)

                return scorecard_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SuggestionOutScorecardType0 | Unset, data)

        scorecard = _parse_scorecard(d.pop("scorecard", UNSET))

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        suggestion_out = cls(
            id=id,
            name=name,
            platform_id=platform_id,
            rule_type=rule_type,
            action=action,
            condition=condition,
            description=description,
            is_active=is_active,
            priority=priority,
            scorecard=scorecard,
            source=source,
        )

        suggestion_out.additional_properties = d
        return suggestion_out

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
