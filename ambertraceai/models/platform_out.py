from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.platform_out_config_type_0 import PlatformOutConfigType0
    from ..models.platform_out_neural_config_type_0 import PlatformOutNeuralConfigType0


T = TypeVar("T", bound="PlatformOut")


@_attrs_define
class PlatformOut:
    """
    Attributes:
        domain_id (int):
        id (int):
        name (str):
        organisation_id (str):
        status (str):
        config (None | PlatformOutConfigType0 | Unset):
        created_at (None | str | Unset):
        description (None | str | Unset):
        neural_config (None | PlatformOutNeuralConfigType0 | Unset):
        updated_at (None | str | Unset):
        verified_min_confidence (float | None | Unset): The certified-fact confidence threshold τ, surfaced from
            neural_config.
        verified_profile (bool | Unset): Whether this platform runs in the verified profile (proof certificates and
            certified-fact gating). If a verified build was downgraded via override_verification_gate, this is False and
            ``config.verification_gate_violations`` records why. Default: False.
        version (int | Unset):  Default: 1.
    """

    domain_id: int
    id: int
    name: str
    organisation_id: str
    status: str
    config: None | PlatformOutConfigType0 | Unset = UNSET
    created_at: None | str | Unset = UNSET
    description: None | str | Unset = UNSET
    neural_config: None | PlatformOutNeuralConfigType0 | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    verified_min_confidence: float | None | Unset = UNSET
    verified_profile: bool | Unset = False
    version: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.platform_out_config_type_0 import PlatformOutConfigType0
        from ..models.platform_out_neural_config_type_0 import (
            PlatformOutNeuralConfigType0,
        )

        domain_id = self.domain_id

        id = self.id

        name = self.name

        organisation_id = self.organisation_id

        status = self.status

        config: dict[str, Any] | None | Unset
        if isinstance(self.config, Unset):
            config = UNSET
        elif isinstance(self.config, PlatformOutConfigType0):
            config = self.config.to_dict()
        else:
            config = self.config

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

        neural_config: dict[str, Any] | None | Unset
        if isinstance(self.neural_config, Unset):
            neural_config = UNSET
        elif isinstance(self.neural_config, PlatformOutNeuralConfigType0):
            neural_config = self.neural_config.to_dict()
        else:
            neural_config = self.neural_config

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        verified_min_confidence: float | None | Unset
        if isinstance(self.verified_min_confidence, Unset):
            verified_min_confidence = UNSET
        else:
            verified_min_confidence = self.verified_min_confidence

        verified_profile = self.verified_profile

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
                "id": id,
                "name": name,
                "organisation_id": organisation_id,
                "status": status,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if description is not UNSET:
            field_dict["description"] = description
        if neural_config is not UNSET:
            field_dict["neural_config"] = neural_config
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at
        if verified_min_confidence is not UNSET:
            field_dict["verified_min_confidence"] = verified_min_confidence
        if verified_profile is not UNSET:
            field_dict["verified_profile"] = verified_profile
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_out_config_type_0 import PlatformOutConfigType0
        from ..models.platform_out_neural_config_type_0 import (
            PlatformOutNeuralConfigType0,
        )

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        id = d.pop("id")

        name = d.pop("name")

        organisation_id = d.pop("organisation_id")

        status = d.pop("status")

        def _parse_config(data: object) -> None | PlatformOutConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                config_type_0 = PlatformOutConfigType0.from_dict(data)

                return config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlatformOutConfigType0 | Unset, data)

        config = _parse_config(d.pop("config", UNSET))

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

        def _parse_neural_config(
            data: object,
        ) -> None | PlatformOutNeuralConfigType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                neural_config_type_0 = PlatformOutNeuralConfigType0.from_dict(data)

                return neural_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlatformOutNeuralConfigType0 | Unset, data)

        neural_config = _parse_neural_config(d.pop("neural_config", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        def _parse_verified_min_confidence(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        verified_min_confidence = _parse_verified_min_confidence(
            d.pop("verified_min_confidence", UNSET)
        )

        verified_profile = d.pop("verified_profile", UNSET)

        version = d.pop("version", UNSET)

        platform_out = cls(
            domain_id=domain_id,
            id=id,
            name=name,
            organisation_id=organisation_id,
            status=status,
            config=config,
            created_at=created_at,
            description=description,
            neural_config=neural_config,
            updated_at=updated_at,
            verified_min_confidence=verified_min_confidence,
            verified_profile=verified_profile,
            version=version,
        )

        platform_out.additional_properties = d
        return platform_out

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
