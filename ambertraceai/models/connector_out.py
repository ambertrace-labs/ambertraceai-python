from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_field_out import ConfigFieldOut


T = TypeVar("T", bound="ConnectorOut")


@_attrs_define
class ConnectorOut:
    """
    Attributes:
        description (str):
        type_ (str):
        asset_classes (list[str] | Unset):
        config_schema (list[ConfigFieldOut] | Unset): Machine-readable config schema: one entry per accepted config key.
            Empty for connectors that have not declared a schema yet.
        countries (list[str] | Unset):
        currencies (list[str] | Unset):
        entitlement (str | Unset):  Default: 'restricted'.
        redistributable (bool | Unset):  Default: False.
        requires (list[str] | Unset):
        source_notice (None | str | Unset): Licence notice that must be shown wherever this source's data -- or a
            derivative of it -- is delivered. Some source licences impose a per-access disclosure duty that a signup-time
            acceptance or a static legal footer does not discharge. None when no notice is due.
    """

    description: str
    type_: str
    asset_classes: list[str] | Unset = UNSET
    config_schema: list[ConfigFieldOut] | Unset = UNSET
    countries: list[str] | Unset = UNSET
    currencies: list[str] | Unset = UNSET
    entitlement: str | Unset = "restricted"
    redistributable: bool | Unset = False
    requires: list[str] | Unset = UNSET
    source_notice: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        description = self.description

        type_ = self.type_

        asset_classes: list[str] | Unset = UNSET
        if not isinstance(self.asset_classes, Unset):
            asset_classes = self.asset_classes

        config_schema: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.config_schema, Unset):
            config_schema = []
            for config_schema_item_data in self.config_schema:
                config_schema_item = config_schema_item_data.to_dict()
                config_schema.append(config_schema_item)

        countries: list[str] | Unset = UNSET
        if not isinstance(self.countries, Unset):
            countries = self.countries

        currencies: list[str] | Unset = UNSET
        if not isinstance(self.currencies, Unset):
            currencies = self.currencies

        entitlement = self.entitlement

        redistributable = self.redistributable

        requires: list[str] | Unset = UNSET
        if not isinstance(self.requires, Unset):
            requires = self.requires

        source_notice: None | str | Unset
        if isinstance(self.source_notice, Unset):
            source_notice = UNSET
        else:
            source_notice = self.source_notice

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "description": description,
                "type": type_,
            }
        )
        if asset_classes is not UNSET:
            field_dict["asset_classes"] = asset_classes
        if config_schema is not UNSET:
            field_dict["config_schema"] = config_schema
        if countries is not UNSET:
            field_dict["countries"] = countries
        if currencies is not UNSET:
            field_dict["currencies"] = currencies
        if entitlement is not UNSET:
            field_dict["entitlement"] = entitlement
        if redistributable is not UNSET:
            field_dict["redistributable"] = redistributable
        if requires is not UNSET:
            field_dict["requires"] = requires
        if source_notice is not UNSET:
            field_dict["source_notice"] = source_notice

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.config_field_out import ConfigFieldOut

        d = dict(src_dict)
        description = d.pop("description")

        type_ = d.pop("type")

        asset_classes = cast(list[str], d.pop("asset_classes", UNSET))

        _config_schema = d.pop("config_schema", UNSET)
        config_schema: list[ConfigFieldOut] | Unset = UNSET
        if _config_schema is not UNSET:
            config_schema = []
            for config_schema_item_data in _config_schema:
                config_schema_item = ConfigFieldOut.from_dict(config_schema_item_data)

                config_schema.append(config_schema_item)

        countries = cast(list[str], d.pop("countries", UNSET))

        currencies = cast(list[str], d.pop("currencies", UNSET))

        entitlement = d.pop("entitlement", UNSET)

        redistributable = d.pop("redistributable", UNSET)

        requires = cast(list[str], d.pop("requires", UNSET))

        def _parse_source_notice(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        source_notice = _parse_source_notice(d.pop("source_notice", UNSET))

        connector_out = cls(
            description=description,
            type_=type_,
            asset_classes=asset_classes,
            config_schema=config_schema,
            countries=countries,
            currencies=currencies,
            entitlement=entitlement,
            redistributable=redistributable,
            requires=requires,
            source_notice=source_notice,
        )

        connector_out.additional_properties = d
        return connector_out

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
