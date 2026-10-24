from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.decision_table_in import DecisionTableIn


T = TypeVar("T", bound="DomainCreate")


@_attrs_define
class DomainCreate:
    """
    Attributes:
        name (str):
        decision_table (DecisionTableIn | None | Unset): Optional declared Decision Table (same body as PUT
            /domains/{id}/decision-table): validated, then stored and marked applied='confirmed'. Shorthand for create +
            set_decision_table.
        decision_vocabulary (Any | None | Unset): Rejected with 400. Declare outcomes with decision_table instead.
        description (str | Unset):  Default: ''.
        team_id (int | None | Unset): Required when visibility='team'; the caller must be a member.
        visibility (None | str | Unset): Sharing audience: 'user' (private, default) | 'team' | 'org'.
    """

    name: str
    decision_table: DecisionTableIn | None | Unset = UNSET
    decision_vocabulary: Any | None | Unset = UNSET
    description: str | Unset = ""
    team_id: int | None | Unset = UNSET
    visibility: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.decision_table_in import DecisionTableIn

        name = self.name

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, DecisionTableIn):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        decision_vocabulary: Any | None | Unset
        if isinstance(self.decision_vocabulary, Unset):
            decision_vocabulary = UNSET
        else:
            decision_vocabulary = self.decision_vocabulary

        description = self.description

        team_id: int | None | Unset
        if isinstance(self.team_id, Unset):
            team_id = UNSET
        else:
            team_id = self.team_id

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        else:
            visibility = self.visibility

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
            }
        )
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table
        if decision_vocabulary is not UNSET:
            field_dict["decision_vocabulary"] = decision_vocabulary
        if description is not UNSET:
            field_dict["description"] = description
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.decision_table_in import DecisionTableIn

        d = dict(src_dict)
        name = d.pop("name")

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

        def _parse_decision_vocabulary(data: object) -> Any | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Any | None | Unset, data)

        decision_vocabulary = _parse_decision_vocabulary(d.pop("decision_vocabulary", UNSET))

        description = d.pop("description", UNSET)

        def _parse_team_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        team_id = _parse_team_id(d.pop("team_id", UNSET))

        def _parse_visibility(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))

        domain_create = cls(
            name=name,
            decision_table=decision_table,
            decision_vocabulary=decision_vocabulary,
            description=description,
            team_id=team_id,
            visibility=visibility,
        )

        domain_create.additional_properties = d
        return domain_create

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
