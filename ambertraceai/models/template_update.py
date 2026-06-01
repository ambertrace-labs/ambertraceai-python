from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.template_update_params_type_0 import TemplateUpdateParamsType0


T = TypeVar("T", bound="TemplateUpdate")


@_attrs_define
class TemplateUpdate:
    """
    Attributes:
        action_field (None | str | Unset):
        action_type (None | str | Unset):
        category (None | str | Unset):
        condition_field (None | str | Unset):
        condition_operator (None | str | Unset):
        is_active (bool | None | Unset):
        name (None | str | Unset):
        name_template (None | str | Unset):
        param_to_action_value (None | str | Unset):
        param_to_condition_value (None | str | Unset):
        params (None | TemplateUpdateParamsType0 | Unset):
    """

    action_field: None | str | Unset = UNSET
    action_type: None | str | Unset = UNSET
    category: None | str | Unset = UNSET
    condition_field: None | str | Unset = UNSET
    condition_operator: None | str | Unset = UNSET
    is_active: bool | None | Unset = UNSET
    name: None | str | Unset = UNSET
    name_template: None | str | Unset = UNSET
    param_to_action_value: None | str | Unset = UNSET
    param_to_condition_value: None | str | Unset = UNSET
    params: None | TemplateUpdateParamsType0 | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.template_update_params_type_0 import TemplateUpdateParamsType0

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
        elif isinstance(self.params, TemplateUpdateParamsType0):
            params = self.params.to_dict()
        else:
            params = self.params

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if action_field is not UNSET:
            field_dict["action_field"] = action_field
        if action_type is not UNSET:
            field_dict["action_type"] = action_type
        if category is not UNSET:
            field_dict["category"] = category
        if condition_field is not UNSET:
            field_dict["condition_field"] = condition_field
        if condition_operator is not UNSET:
            field_dict["condition_operator"] = condition_operator
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if name is not UNSET:
            field_dict["name"] = name
        if name_template is not UNSET:
            field_dict["name_template"] = name_template
        if param_to_action_value is not UNSET:
            field_dict["param_to_action_value"] = param_to_action_value
        if param_to_condition_value is not UNSET:
            field_dict["param_to_condition_value"] = param_to_condition_value
        if params is not UNSET:
            field_dict["params"] = params

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.template_update_params_type_0 import TemplateUpdateParamsType0

        d = dict(src_dict)

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

        def _parse_params(data: object) -> None | TemplateUpdateParamsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                params_type_0 = TemplateUpdateParamsType0.from_dict(data)

                return params_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | TemplateUpdateParamsType0 | Unset, data)

        params = _parse_params(d.pop("params", UNSET))

        template_update = cls(
            action_field=action_field,
            action_type=action_type,
            category=category,
            condition_field=condition_field,
            condition_operator=condition_operator,
            is_active=is_active,
            name=name,
            name_template=name_template,
            param_to_action_value=param_to_action_value,
            param_to_condition_value=param_to_condition_value,
            params=params,
        )

        template_update.additional_properties = d
        return template_update

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
