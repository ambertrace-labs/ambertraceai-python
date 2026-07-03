from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.dataset_out_schema_info_type_0 import DatasetOutSchemaInfoType0


T = TypeVar("T", bound="DatasetOut")


@_attrs_define
class DatasetOut:
    """
    Attributes:
        domain_id (int):
        id (int):
        name (str):
        organisation_id (str):
        source_type (str):
        status (str):
        column_count (int | None | Unset):
        created_at (None | str | Unset):
        decision_column (None | str | Unset):
        description (None | str | Unset):
        relation_join_key (None | str | Unset):
        relation_name (None | str | Unset):
        row_count (int | None | Unset):
        schema_info (DatasetOutSchemaInfoType0 | None | Unset):
        updated_at (None | str | Unset):
    """

    domain_id: int
    id: int
    name: str
    organisation_id: str
    source_type: str
    status: str
    column_count: int | None | Unset = UNSET
    created_at: None | str | Unset = UNSET
    decision_column: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    relation_join_key: None | str | Unset = UNSET
    relation_name: None | str | Unset = UNSET
    row_count: int | None | Unset = UNSET
    schema_info: DatasetOutSchemaInfoType0 | None | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.dataset_out_schema_info_type_0 import DatasetOutSchemaInfoType0

        domain_id = self.domain_id

        id = self.id

        name = self.name

        organisation_id = self.organisation_id

        source_type = self.source_type

        status = self.status

        column_count: int | None | Unset
        if isinstance(self.column_count, Unset):
            column_count = UNSET
        else:
            column_count = self.column_count

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        decision_column: None | str | Unset
        if isinstance(self.decision_column, Unset):
            decision_column = UNSET
        else:
            decision_column = self.decision_column

        description: None | str | Unset
        if isinstance(self.description, Unset):
            description = UNSET
        else:
            description = self.description

        relation_join_key: None | str | Unset
        if isinstance(self.relation_join_key, Unset):
            relation_join_key = UNSET
        else:
            relation_join_key = self.relation_join_key

        relation_name: None | str | Unset
        if isinstance(self.relation_name, Unset):
            relation_name = UNSET
        else:
            relation_name = self.relation_name

        row_count: int | None | Unset
        if isinstance(self.row_count, Unset):
            row_count = UNSET
        else:
            row_count = self.row_count

        schema_info: dict[str, Any] | None | Unset
        if isinstance(self.schema_info, Unset):
            schema_info = UNSET
        elif isinstance(self.schema_info, DatasetOutSchemaInfoType0):
            schema_info = self.schema_info.to_dict()
        else:
            schema_info = self.schema_info

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "id": id,
                "name": name,
                "organisation_id": organisation_id,
                "source_type": source_type,
                "status": status,
            }
        )
        if column_count is not UNSET:
            field_dict["column_count"] = column_count
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if decision_column is not UNSET:
            field_dict["decision_column"] = decision_column
        if description is not UNSET:
            field_dict["description"] = description
        if relation_join_key is not UNSET:
            field_dict["relation_join_key"] = relation_join_key
        if relation_name is not UNSET:
            field_dict["relation_name"] = relation_name
        if row_count is not UNSET:
            field_dict["row_count"] = row_count
        if schema_info is not UNSET:
            field_dict["schema_info"] = schema_info
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.dataset_out_schema_info_type_0 import DatasetOutSchemaInfoType0

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        id = d.pop("id")

        name = d.pop("name")

        organisation_id = d.pop("organisation_id")

        source_type = d.pop("source_type")

        status = d.pop("status")

        def _parse_column_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        column_count = _parse_column_count(d.pop("column_count", UNSET))

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_decision_column(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        decision_column = _parse_decision_column(d.pop("decision_column", UNSET))

        def _parse_description(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        description = _parse_description(d.pop("description", UNSET))

        def _parse_relation_join_key(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        relation_join_key = _parse_relation_join_key(d.pop("relation_join_key", UNSET))

        def _parse_relation_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        relation_name = _parse_relation_name(d.pop("relation_name", UNSET))

        def _parse_row_count(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        row_count = _parse_row_count(d.pop("row_count", UNSET))

        def _parse_schema_info(
            data: object,
        ) -> DatasetOutSchemaInfoType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                schema_info_type_0 = DatasetOutSchemaInfoType0.from_dict(data)

                return schema_info_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DatasetOutSchemaInfoType0 | None | Unset, data)

        schema_info = _parse_schema_info(d.pop("schema_info", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        dataset_out = cls(
            domain_id=domain_id,
            id=id,
            name=name,
            organisation_id=organisation_id,
            source_type=source_type,
            status=status,
            column_count=column_count,
            created_at=created_at,
            decision_column=decision_column,
            description=description,
            relation_join_key=relation_join_key,
            relation_name=relation_name,
            row_count=row_count,
            schema_info=schema_info,
            updated_at=updated_at,
        )

        dataset_out.additional_properties = d
        return dataset_out

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
