from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StalenessOut")


@_attrs_define
class StalenessOut:
    """Whether a config's training data has changed since its active model was trained.

    Attributes:
        data_changed (bool): True when the current dataset fingerprint differs from the one the active model trained on.
        model_version (int): ID of the active model version.
        current_data_fingerprint (None | str | Unset): SHA-256 over the content of the datasets a retrain would use now
            (null if unverifiable).
        current_dataset_ids (list[int] | Unset): IDs of the datasets a retrain would use now.
        trained_at (None | str | Unset): When the active model was trained (ISO 8601, UTC).
        training_data_fingerprint (None | str | Unset): SHA-256 recorded when the active model was trained (null for
            models trained before provenance was recorded).
    """

    data_changed: bool
    model_version: int
    current_data_fingerprint: None | str | Unset = UNSET
    current_dataset_ids: list[int] | Unset = UNSET
    trained_at: None | str | Unset = UNSET
    training_data_fingerprint: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data_changed = self.data_changed

        model_version = self.model_version

        current_data_fingerprint: None | str | Unset
        if isinstance(self.current_data_fingerprint, Unset):
            current_data_fingerprint = UNSET
        else:
            current_data_fingerprint = self.current_data_fingerprint

        current_dataset_ids: list[int] | Unset = UNSET
        if not isinstance(self.current_dataset_ids, Unset):
            current_dataset_ids = self.current_dataset_ids

        trained_at: None | str | Unset
        if isinstance(self.trained_at, Unset):
            trained_at = UNSET
        else:
            trained_at = self.trained_at

        training_data_fingerprint: None | str | Unset
        if isinstance(self.training_data_fingerprint, Unset):
            training_data_fingerprint = UNSET
        else:
            training_data_fingerprint = self.training_data_fingerprint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "data_changed": data_changed,
                "model_version": model_version,
            }
        )
        if current_data_fingerprint is not UNSET:
            field_dict["current_data_fingerprint"] = current_data_fingerprint
        if current_dataset_ids is not UNSET:
            field_dict["current_dataset_ids"] = current_dataset_ids
        if trained_at is not UNSET:
            field_dict["trained_at"] = trained_at
        if training_data_fingerprint is not UNSET:
            field_dict["training_data_fingerprint"] = training_data_fingerprint

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        data_changed = d.pop("data_changed")

        model_version = d.pop("model_version")

        def _parse_current_data_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        current_data_fingerprint = _parse_current_data_fingerprint(d.pop("current_data_fingerprint", UNSET))

        current_dataset_ids = cast(list[int], d.pop("current_dataset_ids", UNSET))

        def _parse_trained_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        trained_at = _parse_trained_at(d.pop("trained_at", UNSET))

        def _parse_training_data_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        training_data_fingerprint = _parse_training_data_fingerprint(d.pop("training_data_fingerprint", UNSET))

        staleness_out = cls(
            data_changed=data_changed,
            model_version=model_version,
            current_data_fingerprint=current_data_fingerprint,
            current_dataset_ids=current_dataset_ids,
            trained_at=trained_at,
            training_data_fingerprint=training_data_fingerprint,
        )

        staleness_out.additional_properties = d
        return staleness_out

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
