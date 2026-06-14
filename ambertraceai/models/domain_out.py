from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DomainOut")


@_attrs_define
class DomainOut:
    """
    Attributes:
        id (int):
        name (str):
        organisation_id (str):
        status (str):
        created_at (None | str | Unset):
        description (None | str | Unset):
        owner_user_id (int | None | Unset):
        team_id (int | None | Unset):
        updated_at (None | str | Unset):
        visibility (str | Unset):  Default: 'user'.
    """

    id: int
    name: str
    organisation_id: str
    status: str
    created_at: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    owner_user_id: int | None | Unset = UNSET
    team_id: int | None | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    visibility: str | Unset = "user"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        name = self.name

        organisation_id = self.organisation_id

        status = self.status

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

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
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
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

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = d.pop("id")

        name = d.pop("name")

        organisation_id = d.pop("organisation_id")

        status = d.pop("status")

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

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

        domain_out = cls(
            id=id,
            name=name,
            organisation_id=organisation_id,
            status=status,
            created_at=created_at,
            description=description,
            owner_user_id=owner_user_id,
            team_id=team_id,
            updated_at=updated_at,
            visibility=visibility,
        )

        domain_out.additional_properties = d
        return domain_out

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
