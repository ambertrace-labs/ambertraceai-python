from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_create_request_action import RuleCreateRequestAction
    from ..models.rule_create_request_condition import RuleCreateRequestCondition


T = TypeVar("T", bound="RuleCreateRequest")


@_attrs_define
class RuleCreateRequest:
    """Create an active or pending symbolic rule manually.

    Attributes:
        action (RuleCreateRequestAction): Structured THEN clause (what fires on a match).
        condition (RuleCreateRequestCondition): Structured IF clause (the trigger condition).
        name (str): Human-readable rule name.
        description (None | str | Unset): What the rule does and why.
        is_active (bool | Unset): Whether the rule should fire immediately. On a verified-profile platform an active
            rule must pass the verification gate or the request is rejected with 409. Default: True.
        priority (int | None | Unset): Evaluation priority (higher first). Defaults to 5.
        rule_type (str | Unset): Rule category, e.g. 'constraint', 'manual', 'inference'. Default: 'constraint'.
    """

    action: RuleCreateRequestAction
    condition: RuleCreateRequestCondition
    name: str
    description: None | str | Unset = UNSET
    is_active: bool | Unset = True
    priority: int | None | Unset = UNSET
    rule_type: str | Unset = "constraint"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        action = self.action.to_dict()

        condition = self.condition.to_dict()

        name = self.name

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        is_active = self.is_active

        priority: int | None | Unset
        if isinstance(self.priority, Unset):
            priority = UNSET
        else:
            priority = self.priority

        rule_type = self.rule_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "condition": condition,
                "name": name,
            }
        )
        if description is not UNSET:
            field_dict["description"] = description
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if priority is not UNSET:
            field_dict["priority"] = priority
        if rule_type is not UNSET:
            field_dict["rule_type"] = rule_type

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_create_request_action import RuleCreateRequestAction
        from ..models.rule_create_request_condition import RuleCreateRequestCondition

        d = dict(src_dict)
        action = RuleCreateRequestAction.from_dict(d.pop("action"))

        condition = RuleCreateRequestCondition.from_dict(d.pop("condition"))

        name = d.pop("name")

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        is_active = d.pop("is_active", UNSET)

        def _parse_priority(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        priority = _parse_priority(d.pop("priority", UNSET))

        rule_type = d.pop("rule_type", UNSET)

        rule_create_request = cls(
            action=action,
            condition=condition,
            name=name,
            description=description,
            is_active=is_active,
            priority=priority,
            rule_type=rule_type,
        )

        rule_create_request.additional_properties = d
        return rule_create_request

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
