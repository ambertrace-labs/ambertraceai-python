from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decision_table_in import DecisionTableIn


T = TypeVar("T", bound="CompilePolicyRequest")


@_attrs_define
class CompilePolicyRequest:
    """
    Attributes:
        policy_text (str): The governance policy in natural language (the rules to author)
        decision_table (DecisionTableIn | None | Unset): Optional Decision Table (same body as PUT
            /domains/{id}/decision-table): the outcomes the gate may decide, e.g. permit / escalate / deny with `order` and
            `permits`. A gate table is a ladder with at least one permitting and one non-permitting row. Omitted -> the
            product's binary table {permit (default), deny}.
    """

    policy_text: str
    decision_table: DecisionTableIn | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.decision_table_in import DecisionTableIn

        policy_text = self.policy_text

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, DecisionTableIn):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "policy_text": policy_text,
            }
        )
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.decision_table_in import DecisionTableIn

        d = dict(src_dict)
        policy_text = d.pop("policy_text")

        def _parse_decision_table(data: object) -> DecisionTableIn | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_table_type_0 = DecisionTableIn.from_dict(data)

                return decision_table_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DecisionTableIn | None | Unset, data)

        decision_table = _parse_decision_table(d.pop("decision_table", UNSET))

        compile_policy_request = cls(
            policy_text=policy_text,
            decision_table=decision_table,
        )

        compile_policy_request.additional_properties = d
        return compile_policy_request

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
