from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rule_out_action_type_0 import RuleOutActionType0
    from ..models.rule_out_condition_type_0 import RuleOutConditionType0
    from ..models.rule_out_scorecard_type_0 import RuleOutScorecardType0
    from ..models.schema_reconciliation import SchemaReconciliation


T = TypeVar("T", bound="RuleOut")


@_attrs_define
class RuleOut:
    """A symbolic rule on a platform (active or inactive).

    Attributes:
        id (int): Rule ID.
        name (str): Human-readable rule name.
        platform_id (int): Owning platform ID.
        rule_type (str): Rule category, e.g. 'constraint', 'inference', 'manual'.
        action (None | RuleOutActionType0 | Unset): Structured THEN clause (what fires on a match).
        condition (None | RuleOutConditionType0 | Unset): Structured IF clause (the trigger condition).
        description (None | str | Unset): What the rule does and why.
        is_active (bool | Unset): Whether the rule currently fires in queries. Default: False.
        priority (int | Unset): Evaluation priority (higher first). Default: 0.
        schema_reconciliation (None | SchemaReconciliation | Unset): Column-mapping report for a create/update (data-
            driven ontology §2.3): which field references mapped to which real columns. Present on createRule/updateRule
            responses; null on list/get.
        scorecard (None | RuleOutScorecardType0 | Unset): Per-gate verdicts from rule discovery, if any.
        source (None | str | Unset): Provenance, e.g. 'manual', 'auto', 'llm_approved'.
    """

    id: int
    name: str
    platform_id: int
    rule_type: str
    action: None | RuleOutActionType0 | Unset = UNSET
    condition: None | RuleOutConditionType0 | Unset = UNSET
    description: None | str | Unset = UNSET
    is_active: bool | Unset = False
    priority: int | Unset = 0
    schema_reconciliation: None | SchemaReconciliation | Unset = UNSET
    scorecard: None | RuleOutScorecardType0 | Unset = UNSET
    source: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.rule_out_action_type_0 import RuleOutActionType0
        from ..models.rule_out_condition_type_0 import RuleOutConditionType0
        from ..models.rule_out_scorecard_type_0 import RuleOutScorecardType0
        from ..models.schema_reconciliation import SchemaReconciliation

        id = self.id

        name = self.name

        platform_id = self.platform_id

        rule_type = self.rule_type

        action: dict[str, Any] | None | Unset
        if isinstance(self.action, Unset):
            action = UNSET
        elif isinstance(self.action, RuleOutActionType0):
            action = self.action.to_dict()
        else:
            action = self.action

        condition: dict[str, Any] | None | Unset
        if isinstance(self.condition, Unset):
            condition = UNSET
        elif isinstance(self.condition, RuleOutConditionType0):
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

        schema_reconciliation: dict[str, Any] | None | Unset
        if isinstance(self.schema_reconciliation, Unset):
            schema_reconciliation = UNSET
        elif isinstance(self.schema_reconciliation, SchemaReconciliation):
            schema_reconciliation = self.schema_reconciliation.to_dict()
        else:
            schema_reconciliation = self.schema_reconciliation

        scorecard: dict[str, Any] | None | Unset
        if isinstance(self.scorecard, Unset):
            scorecard = UNSET
        elif isinstance(self.scorecard, RuleOutScorecardType0):
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
        if schema_reconciliation is not UNSET:
            field_dict["schema_reconciliation"] = schema_reconciliation
        if scorecard is not UNSET:
            field_dict["scorecard"] = scorecard
        if source is not UNSET:
            field_dict["source"] = source

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.rule_out_action_type_0 import RuleOutActionType0
        from ..models.rule_out_condition_type_0 import RuleOutConditionType0
        from ..models.rule_out_scorecard_type_0 import RuleOutScorecardType0
        from ..models.schema_reconciliation import SchemaReconciliation

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        platform_id = d.pop("platform_id")

        rule_type = d.pop("rule_type")

        def _parse_action(data: object) -> None | RuleOutActionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                action_type_0 = RuleOutActionType0.from_dict(data)

                return action_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleOutActionType0 | Unset, data)

        action = _parse_action(d.pop("action", UNSET))

        def _parse_condition(data: object) -> None | RuleOutConditionType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                condition_type_0 = RuleOutConditionType0.from_dict(data)

                return condition_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleOutConditionType0 | Unset, data)

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

        def _parse_schema_reconciliation(
            data: object,
        ) -> None | SchemaReconciliation | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schema_reconciliation_type_0 = SchemaReconciliation.from_dict(data)

                return schema_reconciliation_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | SchemaReconciliation | Unset, data)

        schema_reconciliation = _parse_schema_reconciliation(
            d.pop("schema_reconciliation", UNSET)
        )

        def _parse_scorecard(data: object) -> None | RuleOutScorecardType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scorecard_type_0 = RuleOutScorecardType0.from_dict(data)

                return scorecard_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | RuleOutScorecardType0 | Unset, data)

        scorecard = _parse_scorecard(d.pop("scorecard", UNSET))

        def _parse_source(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source = _parse_source(d.pop("source", UNSET))

        rule_out = cls(
            id=id,
            name=name,
            platform_id=platform_id,
            rule_type=rule_type,
            action=action,
            condition=condition,
            description=description,
            is_active=is_active,
            priority=priority,
            schema_reconciliation=schema_reconciliation,
            scorecard=scorecard,
            source=source,
        )

        rule_out.additional_properties = d
        return rule_out

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
