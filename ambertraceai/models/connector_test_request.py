from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.connector_test_request_config import ConnectorTestRequestConfig


T = TypeVar("T", bound="ConnectorTestRequest")


@_attrs_define
class ConnectorTestRequest:
    """
    Attributes:
        connector_type (str):
        config (ConnectorTestRequestConfig | Unset):
    """

    connector_type: str
    config: ConnectorTestRequestConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        connector_type = self.connector_type

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "connector_type": connector_type,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.connector_test_request_config import ConnectorTestRequestConfig

        d = dict(src_dict)
        connector_type = d.pop("connector_type")

        _config = d.pop("config", UNSET)
        config: ConnectorTestRequestConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = ConnectorTestRequestConfig.from_dict(_config)

        connector_test_request = cls(
            connector_type=connector_type,
            config=config,
        )

        connector_test_request.additional_properties = d
        return connector_test_request

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
