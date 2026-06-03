from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_update_request_action_type_0 import RuleUpdateRequestActionType0
    from ..models.rule_update_request_condition_type_0 import (
        RuleUpdateRequestConditionType0,
    )


T = TypeVar("T", bound="RuleUpdateRequest")


@_attrs_define
class RuleUpdateRequest:
    """Patch a subset of a rule's fields. Only provided fields are applied.

    Attributes:
        action (None | RuleUpdateRequestActionType0 | Unset): Replacement THEN clause.
        condition (None | RuleUpdateRequestConditionType0 | Unset): Replacement IF clause.
        description (None | str | Unset): New description.
        is_active (bool | None | Unset): Activate (true) or deactivate (false) the rule. Activating — or editing
            condition/action while active — on a verified-profile platform re-runs the verified gate and may reject with
            409. Deactivating is always permitted.
        name (None | str | Unset): New name.
        priority (int | None | Unset): New evaluation priority.
    """

    action: None | RuleUpdateRequestActionType0 | Unset = UNSET
    condition: None | RuleUpdateRequestConditionType0 | Unset = UNSET
    description: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    priority: int | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_update_request_action_type_0 import (
            RuleUpdateRequestActionType0,
        )
        from ..models.rule_update_request_condition_type_0 import (
            RuleUpdateRequestConditionType0,
        )

        action: dict[str, Any] | None | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        elif isinstance(self.action, RuleUpdateRequestActionType0):
            action = self.action.to_dict()
        else:
            action = self.action

        condition: dict[str, Any] | None | Unset
        if isinstance(self.condition, Unset):
            condition = UNSET
        elif isinstance(self.condition, RuleUpdateRequestConditionType0):
            condition = self.condition.to_dict()
        else:
            condition = self.condition

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_active: bool | None | Unset
        if isinstance(self.is_active, Unset):
            is_active = UNSET
        else:
            is_active = self.is_active

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        priority: int | None | Unset
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action is not UNSET:
            field_dict["action"] = action
        if condition is not UNSET:
            field_dict["condition"] = condition
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if priority is not UNSET:
            field_dict["priority"] = priority

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_update_request_action_type_0 import (
            RuleUpdateRequestActionType0,
        )
        from ..models.rule_update_request_condition_type_0 import (
            RuleUpdateRequestConditionType0,
        )

        d = dict(src_dict)

        def _parse_action(data: object) -> None | RuleUpdateRequestActionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                action_type_0 = RuleUpdateRequestActionType0.from_dict(data)

                return action_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleUpdateRequestActionType0 | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        def _parse_condition(
            data: object,
        ) -> None | RuleUpdateRequestConditionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                condition_type_0 = RuleUpdateRequestConditionType0.from_dict(data)

                return condition_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleUpdateRequestConditionType0 | Unset, data)

        condition = _parse_condition(d.pop("condition", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_is_active(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        is_active = _parse_is_active(d.pop("is_active", UNSET))

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_priority(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        priority = _parse_priority(d.pop("priority", UNSET))

        rule_update_request = cls(
            action=action,
            condition=condition,
            description=description,
            is_active=is_active,
            name=name,
            priority=priority,
        )

        rule_update_request.additional_properties = d
        return rule_update_request

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
