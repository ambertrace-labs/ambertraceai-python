from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SuggestorSettingsUpdate")


@_attrs_define
class SuggestorSettingsUpdate:
    """
    Attributes:
        suggestor_backend (None | str | Unset):
        suggestor_hosting (None | str | Unset):
        suggestor_max_new_tokens (int | None | Unset):
        suggestor_temperature (float | None | Unset):
        suggestor_timeout_s (int | None | Unset):
        suggestor_top_p (float | None | Unset):
        suggestor_url (None | str | Unset):
    """

    suggestor_backend: None | str | Unset = UNSET
    suggestor_hosting: None | str | Unset = UNSET
    suggestor_max_new_tokens: int | None | Unset = UNSET
    suggestor_temperature: float | None | Unset = UNSET
    suggestor_timeout_s: int | None | Unset = UNSET
    suggestor_top_p: float | None | Unset = UNSET
    suggestor_url: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        suggestor_backend: None | str | Unset
        if isinstance(self.suggestor_backend, Unset):
            suggestor_backend = UNSET
        else:
            suggestor_backend = self.suggestor_backend

        suggestor_hosting: None | str | Unset
        if isinstance(self.suggestor_hosting, Unset):
            suggestor_hosting = UNSET
        else:
            suggestor_hosting = self.suggestor_hosting

        suggestor_max_new_tokens: int | None | Unset
        if isinstance(self.suggestor_max_new_tokens, Unset):
            suggestor_max_new_tokens = UNSET
        else:
            suggestor_max_new_tokens = self.suggestor_max_new_tokens

        suggestor_temperature: float | None | Unset
        if isinstance(self.suggestor_temperature, Unset):
            suggestor_temperature = UNSET
        else:
            suggestor_temperature = self.suggestor_temperature

        suggestor_timeout_s: int | None | Unset
        if isinstance(self.suggestor_timeout_s, Unset):
            suggestor_timeout_s = UNSET
        else:
            suggestor_timeout_s = self.suggestor_timeout_s

        suggestor_top_p: float | None | Unset
        if isinstance(self.suggestor_top_p, Unset):
            suggestor_top_p = UNSET
        else:
            suggestor_top_p = self.suggestor_top_p

        suggestor_url: None | str | Unset
        if isinstance(self.suggestor_url, Unset):
            suggestor_url = UNSET
        else:
            suggestor_url = self.suggestor_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if suggestor_backend is not UNSET:
            field_dict["suggestor_backend"] = suggestor_backend
        if suggestor_hosting is not UNSET:
            field_dict["suggestor_hosting"] = suggestor_hosting
        if suggestor_max_new_tokens is not UNSET:
            field_dict["suggestor_max_new_tokens"] = suggestor_max_new_tokens
        if suggestor_temperature is not UNSET:
            field_dict["suggestor_temperature"] = suggestor_temperature
        if suggestor_timeout_s is not UNSET:
            field_dict["suggestor_timeout_s"] = suggestor_timeout_s
        if suggestor_top_p is not UNSET:
            field_dict["suggestor_top_p"] = suggestor_top_p
        if suggestor_url is not UNSET:
            field_dict["suggestor_url"] = suggestor_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_suggestor_backend(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        suggestor_backend = _parse_suggestor_backend(d.pop("suggestor_backend", UNSET))

        def _parse_suggestor_hosting(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        suggestor_hosting = _parse_suggestor_hosting(d.pop("suggestor_hosting", UNSET))

        def _parse_suggestor_max_new_tokens(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        suggestor_max_new_tokens = _parse_suggestor_max_new_tokens(
            d.pop("suggestor_max_new_tokens", UNSET)
        )

        def _parse_suggestor_temperature(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        suggestor_temperature = _parse_suggestor_temperature(
            d.pop("suggestor_temperature", UNSET)
        )

        def _parse_suggestor_timeout_s(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        suggestor_timeout_s = _parse_suggestor_timeout_s(
            d.pop("suggestor_timeout_s", UNSET)
        )

        def _parse_suggestor_top_p(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        suggestor_top_p = _parse_suggestor_top_p(d.pop("suggestor_top_p", UNSET))

        def _parse_suggestor_url(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        suggestor_url = _parse_suggestor_url(d.pop("suggestor_url", UNSET))

        suggestor_settings_update = cls(
            suggestor_backend=suggestor_backend,
            suggestor_hosting=suggestor_hosting,
            suggestor_max_new_tokens=suggestor_max_new_tokens,
            suggestor_temperature=suggestor_temperature,
            suggestor_timeout_s=suggestor_timeout_s,
            suggestor_top_p=suggestor_top_p,
            suggestor_url=suggestor_url,
        )

        suggestor_settings_update.additional_properties = d
        return suggestor_settings_update

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
