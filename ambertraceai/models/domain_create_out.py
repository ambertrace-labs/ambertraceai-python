from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain_create_out_advisories_item import DomainCreateOutAdvisoriesItem
    from ..models.domain_create_out_decision_table_type_0 import DomainCreateOutDecisionTableType0


T = TypeVar("T", bound="DomainCreateOut")


@_attrs_define
class DomainCreateOut:
    """POST /domains response: DomainOut plus the Decision Table advisories.

    Attributes:
        id (int):
        name (str):
        organisation_id (str):
        status (str):
        advisories (list[DomainCreateOutAdvisoriesItem] | Unset): Advisory notes on a Decision Table submitted at create
            time (create(decision_table=)); each {check, kind, row, message}. Empty when no table is submitted; never blocks
            or alters the table, which is stored exactly as declared.
        created_at (None | str | Unset):
        decision_table (DomainCreateOutDecisionTableType0 | None | Unset): The declared Decision Table {mode, rows:
            [{id, label, order, default, permits, values}], provenance, applied}; null until declared (PUT
            /domains/{id}/decision-table or create(decision_table=)).
        description (None | str | Unset):
        owner_user_id (int | None | Unset):
        team_id (int | None | Unset):
        updated_at (None | str | Unset):
        visibility (str | Unset):  Default: 'user'.
        warning (None | str | Unset): Set when a domain with the same name already exists (it is still created); names
            the existing id and points at domains.get_or_create(). Null otherwise.
    """

    id: int
    name: str
    organisation_id: str
    status: str
    advisories: list[DomainCreateOutAdvisoriesItem] | Unset = UNSET
    created_at: None | str | Unset = UNSET
    decision_table: DomainCreateOutDecisionTableType0 | None | Unset = UNSET
    description: None | str | Unset = UNSET
    owner_user_id: int | None | Unset = UNSET
    team_id: int | None | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    visibility: str | Unset = "user"
    warning: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.domain_create_out_decision_table_type_0 import DomainCreateOutDecisionTableType0

        id = self.id

        name = self.name

        organisation_id = self.organisation_id

        status = self.status

        advisories: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.advisories, Unset):
            advisories = []
            for advisories_item_data in self.advisories:
                advisories_item = advisories_item_data.to_dict()
                advisories.append(advisories_item)

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        decision_table: dict[str, Any] | None | Unset
        if isinstance(self.decision_table, Unset):
            decision_table = UNSET
        elif isinstance(self.decision_table, DomainCreateOutDecisionTableType0):
            decision_table = self.decision_table.to_dict()
        else:
            decision_table = self.decision_table

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        owner_user_id: int | None | Unset
        if isinstance(self.owner_user_id, Unset):
            owner_user_id = UNSET
        else:
            owner_user_id = self.owner_user_id

        team_id: int | None | Unset
        if isinstance(self.team_id, Unset):
            team_id = UNSET
        else:
            team_id = self.team_id

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        visibility = self.visibility

        warning: None | str | Unset
        if isinstance(self.warning, Unset):
            warning = UNSET
        else:
            warning = self.warning

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "name": name,
                "organisation_id": organisation_id,
                "status": status,
            }
        )
        if advisories is not UNSET:
            field_dict["advisories"] = advisories
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if decision_table is not UNSET:
            field_dict["decision_table"] = decision_table
        if description is not UNSET:
            field_dict["description"] = description
        if owner_user_id is not UNSET:
            field_dict["owner_user_id"] = owner_user_id
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if visibility is not UNSET:
            field_dict["visibility"] = visibility
        if warning is not UNSET:
            field_dict["warning"] = warning

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.domain_create_out_advisories_item import DomainCreateOutAdvisoriesItem
        from ..models.domain_create_out_decision_table_type_0 import DomainCreateOutDecisionTableType0

        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        organisation_id = d.pop("organisation_id")

        status = d.pop("status")

        _advisories = d.pop("advisories", UNSET)
        advisories: list[DomainCreateOutAdvisoriesItem] | Unset = UNSET
        if _advisories is not UNSET:
            advisories = []
            for advisories_item_data in _advisories:
                advisories_item = DomainCreateOutAdvisoriesItem.from_dict(advisories_item_data)

                advisories.append(advisories_item)

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_decision_table(data: object) -> DomainCreateOutDecisionTableType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_table_type_0 = DomainCreateOutDecisionTableType0.from_dict(data)

                return decision_table_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DomainCreateOutDecisionTableType0 | None | Unset, data)

        decision_table = _parse_decision_table(d.pop("decision_table", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_owner_user_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        owner_user_id = _parse_owner_user_id(d.pop("owner_user_id", UNSET))

        def _parse_team_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        team_id = _parse_team_id(d.pop("team_id", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        visibility = d.pop("visibility", UNSET)

        def _parse_warning(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        warning = _parse_warning(d.pop("warning", UNSET))

        domain_create_out = cls(
            id=id,
            name=name,
            organisation_id=organisation_id,
            status=status,
            advisories=advisories,
            created_at=created_at,
            decision_table=decision_table,
            description=description,
            owner_user_id=owner_user_id,
            team_id=team_id,
            updated_at=updated_at,
            visibility=visibility,
            warning=warning,
        )

        domain_create_out.additional_properties = d
        return domain_create_out

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
