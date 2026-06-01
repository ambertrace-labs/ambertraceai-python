from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.domain_detail_eval_config_type_0 import DomainDetailEvalConfigType0
    from ..models.domain_detail_ontology_type_0 import DomainDetailOntologyType0
    from ..models.entity_out import EntityOut
    from ..models.relationship_out import RelationshipOut


T = TypeVar("T", bound="DomainDetail")


@_attrs_define
class DomainDetail:
    """
    Attributes:
        id (int):
        name (str):
        organisation_id (str):
        status (str):
        created_at (None | str | Unset):
        description (None | str | Unset):
        entities (list[EntityOut] | Unset):
        eval_config (DomainDetailEvalConfigType0 | None | Unset):
        ontology (DomainDetailOntologyType0 | None | Unset):
        relationships (list[RelationshipOut] | Unset):
        schema_version (int | Unset):  Default: 1.
        updated_at (None | str | Unset):
    """

    id: int
    name: str
    organisation_id: str
    status: str
    created_at: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    entities: list[EntityOut] | Unset = UNSET
    eval_config: DomainDetailEvalConfigType0 | None | Unset = UNSET
    ontology: DomainDetailOntologyType0 | None | Unset = UNSET
    relationships: list[RelationshipOut] | Unset = UNSET
    schema_version: int | Unset = 1
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.domain_detail_eval_config_type_0 import (
            DomainDetailEvalConfigType0,
        )
        from ..models.domain_detail_ontology_type_0 import DomainDetailOntologyType0

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

        entities: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entities, Unset):
            entities = []
            for entities_item_data in self.entities:
                entities_item = entities_item_data.to_dict()
                entities.append(entities_item)

        eval_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_config, Unset):
            eval_config = UNSET
        elif isinstance(self.eval_config, DomainDetailEvalConfigType0):
            eval_config = self.eval_config.to_dict()
        else:
            eval_config = self.eval_config

        ontology: dict[str, Any] | None | Unset
        if isinstance(self.ontology, Unset):
            ontology = UNSET
        elif isinstance(self.ontology, DomainDetailOntologyType0):
            ontology = self.ontology.to_dict()
        else:
            ontology = self.ontology

        relationships: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.relationships, Unset):
            relationships = []
            for relationships_item_data in self.relationships:
                relationships_item = relationships_item_data.to_dict()
                relationships.append(relationships_item)

        schema_version = self.schema_version

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

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
        if entities is not UNSET:
            field_dict["entities"] = entities
        if eval_config is not UNSET:
            field_dict["eval_config"] = eval_config
        if ontology is not UNSET:
            field_dict["ontology"] = ontology
        if relationships is not UNSET:
            field_dict["relationships"] = relationships
        if schema_version is not UNSET:
            field_dict["schema_version"] = schema_version
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.domain_detail_eval_config_type_0 import (
            DomainDetailEvalConfigType0,
        )
        from ..models.domain_detail_ontology_type_0 import DomainDetailOntologyType0
        from ..models.entity_out import EntityOut
        from ..models.relationship_out import RelationshipOut

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

        _entities = d.pop("entities", UNSET)
        entities: list[EntityOut] | Unset = UNSET
        if _entities is not UNSET:
            entities = []
            for entities_item_data in _entities:
                entities_item = EntityOut.from_dict(entities_item_data)

                entities.append(entities_item)

        def _parse_eval_config(
            data: object,
        ) -> DomainDetailEvalConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_config_type_0 = DomainDetailEvalConfigType0.from_dict(data)

                return eval_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DomainDetailEvalConfigType0 | None | Unset, data)

        eval_config = _parse_eval_config(d.pop("eval_config", UNSET))

        def _parse_ontology(data: object) -> DomainDetailOntologyType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ontology_type_0 = DomainDetailOntologyType0.from_dict(data)

                return ontology_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DomainDetailOntologyType0 | None | Unset, data)

        ontology = _parse_ontology(d.pop("ontology", UNSET))

        _relationships = d.pop("relationships", UNSET)
        relationships: list[RelationshipOut] | Unset = UNSET
        if _relationships is not UNSET:
            relationships = []
            for relationships_item_data in _relationships:
                relationships_item = RelationshipOut.from_dict(relationships_item_data)

                relationships.append(relationships_item)

        schema_version = d.pop("schema_version", UNSET)

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        domain_detail = cls(
            id=id,
            name=name,
            organisation_id=organisation_id,
            status=status,
            created_at=created_at,
            description=description,
            entities=entities,
            eval_config=eval_config,
            ontology=ontology,
            relationships=relationships,
            schema_version=schema_version,
            updated_at=updated_at,
        )

        domain_detail.additional_properties = d
        return domain_detail

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
