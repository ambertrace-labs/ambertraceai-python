from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_out_params_type_0 import TemplateOutParamsType0


T = TypeVar("T", bound="TemplateOut")


@_attrs_define
class TemplateOut:
    """
    Attributes:
        domain_id (int):
        id (int):
        name (str):
        template_id (str):
        action_field (None | str | Unset):
        action_type (None | str | Unset):
        author (None | str | Unset):
        category (None | str | Unset):
        condition_field (None | str | Unset):
        condition_operator (None | str | Unset):
        created_at (None | str | Unset):
        is_active (bool | Unset):  Default: True.
        name_template (None | str | Unset):
        param_to_action_value (None | str | Unset):
        param_to_condition_value (None | str | Unset):
        params (None | TemplateOutParamsType0 | Unset):
        updated_at (None | str | Unset):
    """

    domain_id: int
    id: int
    name: str
    template_id: str
    action_field: None | str | Unset = UNSET
    action_type: None | str | Unset = UNSET
    author: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    condition_field: None | str | Unset = UNSET
    condition_operator: None | str | Unset = UNSET
    created_at: None | str | Unset = UNSET
    is_active: bool | Unset = True
    name_template: None | str | Unset = UNSET
    param_to_action_value: None | str | Unset = UNSET
    param_to_condition_value: None | str | Unset = UNSET
    params: None | TemplateOutParamsType0 | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.template_out_params_type_0 import TemplateOutParamsType0

        domain_id = self.domain_id

        id = self.id

        name = self.name

        template_id = self.template_id

        action_field: None | str | Unset
        if isinstance(self.action_field, Unset):
            action_field = UNSET
        else:
            action_field = self.action_field

        action_type: None | str | Unset
        if isinstance(self.action_type, Unset):
            action_type = UNSET
        else:
            action_type = self.action_type

        author: None | str | Unset
        if isinstance(self.author, Unset):
            author = UNSET
        else:
            author = self.author

        category: None | str | Unset
        if isinstance(self.category, Unset):
            category = UNSET
        else:
            category = self.category

        condition_field: None | str | Unset
        if isinstance(self.condition_field, Unset):
            condition_field = UNSET
        else:
            condition_field = self.condition_field

        condition_operator: None | str | Unset
        if isinstance(self.condition_operator, Unset):
            condition_operator = UNSET
        else:
            condition_operator = self.condition_operator

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        is_active = self.is_active

        name_template: None | str | Unset
        if isinstance(self.name_template, Unset):
            name_template = UNSET
        else:
            name_template = self.name_template

        param_to_action_value: None | str | Unset
        if isinstance(self.param_to_action_value, Unset):
            param_to_action_value = UNSET
        else:
            param_to_action_value = self.param_to_action_value

        param_to_condition_value: None | str | Unset
        if isinstance(self.param_to_condition_value, Unset):
            param_to_condition_value = UNSET
        else:
            param_to_condition_value = self.param_to_condition_value

        params: dict[str, Any] | None | Unset
        if isinstance(self.params, Unset):
            params = UNSET
        elif isinstance(self.params, TemplateOutParamsType0):
            params = self.params.to_dict()
        else:
            params = self.params

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
                "template_id": template_id,
            }
        )
        if action_field is not UNSET:
            field_dict["action_field"] = action_field
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if author is not UNSET:
            field_dict["author"] = author
        if category is not UNSET:
            field_dict["category"] = category
        if condition_field is not UNSET:
            field_dict["condition_field"] = condition_field
        if condition_operator is not UNSET:
            field_dict["condition_operator"] = condition_operator
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name_template is not UNSET:
            field_dict["name_template"] = name_template
        if param_to_action_value is not UNSET:
            field_dict["param_to_action_value"] = param_to_action_value
        if param_to_condition_value is not UNSET:
            field_dict["param_to_condition_value"] = param_to_condition_value
        if params is not UNSET:
            field_dict["params"] = params
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.template_out_params_type_0 import TemplateOutParamsType0

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        id = d.pop("id")

        name = d.pop("name")

        template_id = d.pop("template_id")

        def _parse_action_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_field = _parse_action_field(d.pop("action_field", UNSET))

        def _parse_action_type(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        action_type = _parse_action_type(d.pop("action_type", UNSET))

        def _parse_author(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        author = _parse_author(d.pop("author", UNSET))

        def _parse_category(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        category = _parse_category(d.pop("category", UNSET))

        def _parse_condition_field(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        condition_field = _parse_condition_field(d.pop("condition_field", UNSET))

        def _parse_condition_operator(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        condition_operator = _parse_condition_operator(
            d.pop("condition_operator", UNSET)
        )

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        is_active = d.pop("is_active", UNSET)

        def _parse_name_template(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name_template = _parse_name_template(d.pop("name_template", UNSET))

        def _parse_param_to_action_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        param_to_action_value = _parse_param_to_action_value(
            d.pop("param_to_action_value", UNSET)
        )

        def _parse_param_to_condition_value(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        param_to_condition_value = _parse_param_to_condition_value(
            d.pop("param_to_condition_value", UNSET)
        )

        def _parse_params(data: object) -> None | TemplateOutParamsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = TemplateOutParamsType0.from_dict(data)

                return params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TemplateOutParamsType0 | Unset, data)

        params = _parse_params(d.pop("params", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        template_out = cls(
            domain_id=domain_id,
            id=id,
            name=name,
            template_id=template_id,
            action_field=action_field,
            action_type=action_type,
            author=author,
            category=category,
            condition_field=condition_field,
            condition_operator=condition_operator,
            created_at=created_at,
            is_active=is_active,
            name_template=name_template,
            param_to_action_value=param_to_action_value,
            param_to_condition_value=param_to_condition_value,
            params=params,
            updated_at=updated_at,
        )

        template_out.additional_properties = d
        return template_out

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
