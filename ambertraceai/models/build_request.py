from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.build_request_config import BuildRequestConfig


T = TypeVar("T", bound="BuildRequest")


@_attrs_define
class BuildRequest:
    """
    Attributes:
        domain_id (int):
        config (BuildRequestConfig | Unset):
    """

    domain_id: int
    config: BuildRequestConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain_id = self.domain_id

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.build_request_config import BuildRequestConfig

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        _config = d.pop("config", UNSET)
        config: BuildRequestConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = BuildRequestConfig.from_dict(_config)

        build_request = cls(
            domain_id=domain_id,
            config=config,
        )

        build_request.additional_properties = d
        return build_request

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
