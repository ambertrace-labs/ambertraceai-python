from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.model_version_out_metrics_type_0 import ModelVersionOutMetricsType0


T = TypeVar("T", bound="ModelVersionOut")


@_attrs_define
class ModelVersionOut:
    """One trained model version of a prediction config, with its training-data provenance.

    Attributes:
        is_active (bool): True for the version currently serving predictions.
        model_version (int): ID of this model version (the PredictionModel row).
        prediction_config_id (int):
        created_at (None | str | Unset):
        dataset_fingerprint (None | str | Unset): SHA-256 over the content of the training datasets (null for models
            trained before provenance was recorded).
        dataset_ids (list[int] | None | Unset): IDs of the datasets this version was trained on (null for models trained
            before provenance was recorded).
        feature_names (list[str] | None | Unset):
        metrics (ModelVersionOutMetricsType0 | None | Unset): Evaluation metrics recorded at training time.
        trained_at (None | str | Unset): When this version was trained (ISO 8601, UTC).
    """

    is_active: bool
    model_version: int
    prediction_config_id: int
    created_at: None | str | Unset = UNSET
    dataset_fingerprint: None | str | Unset = UNSET
    dataset_ids: list[int] | None | Unset = UNSET
    feature_names: list[str] | None | Unset = UNSET
    metrics: ModelVersionOutMetricsType0 | None | Unset = UNSET
    trained_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.model_version_out_metrics_type_0 import ModelVersionOutMetricsType0

        is_active = self.is_active

        model_version = self.model_version

        prediction_config_id = self.prediction_config_id

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        dataset_fingerprint: None | str | Unset
        if isinstance(self.dataset_fingerprint, Unset):
            dataset_fingerprint = UNSET
        else:
            dataset_fingerprint = self.dataset_fingerprint

        dataset_ids: list[int] | None | Unset
        if isinstance(self.dataset_ids, Unset):
            dataset_ids = UNSET
        elif isinstance(self.dataset_ids, list):
            dataset_ids = self.dataset_ids

        else:
            dataset_ids = self.dataset_ids

        feature_names: list[str] | None | Unset
        if isinstance(self.feature_names, Unset):
            feature_names = UNSET
        elif isinstance(self.feature_names, list):
            feature_names = self.feature_names

        else:
            feature_names = self.feature_names

        metrics: dict[str, Any] | None | Unset
        if isinstance(self.metrics, Unset):
            metrics = UNSET
        elif isinstance(self.metrics, ModelVersionOutMetricsType0):
            metrics = self.metrics.to_dict()
        else:
            metrics = self.metrics

        trained_at: None | str | Unset
        if isinstance(self.trained_at, Unset):
            trained_at = UNSET
        else:
            trained_at = self.trained_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "is_active": is_active,
                "model_version": model_version,
                "prediction_config_id": prediction_config_id,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if dataset_fingerprint is not UNSET:
            field_dict["dataset_fingerprint"] = dataset_fingerprint
        if dataset_ids is not UNSET:
            field_dict["dataset_ids"] = dataset_ids
        if feature_names is not UNSET:
            field_dict["feature_names"] = feature_names
        if metrics is not UNSET:
            field_dict["metrics"] = metrics
        if trained_at is not UNSET:
            field_dict["trained_at"] = trained_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.model_version_out_metrics_type_0 import ModelVersionOutMetricsType0

        d = dict(src_dict)
        is_active = d.pop("is_active")

        model_version = d.pop("model_version")

        prediction_config_id = d.pop("prediction_config_id")

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_dataset_fingerprint(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        dataset_fingerprint = _parse_dataset_fingerprint(d.pop("dataset_fingerprint", UNSET))

        def _parse_dataset_ids(data: object) -> list[int] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                dataset_ids_type_0 = cast(list[int], data)

                return dataset_ids_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[int] | None | Unset, data)

        dataset_ids = _parse_dataset_ids(d.pop("dataset_ids", UNSET))

        def _parse_feature_names(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                feature_names_type_0 = cast(list[str], data)

                return feature_names_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        feature_names = _parse_feature_names(d.pop("feature_names", UNSET))

        def _parse_metrics(data: object) -> ModelVersionOutMetricsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                metrics_type_0 = ModelVersionOutMetricsType0.from_dict(data)

                return metrics_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ModelVersionOutMetricsType0 | None | Unset, data)

        metrics = _parse_metrics(d.pop("metrics", UNSET))

        def _parse_trained_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        trained_at = _parse_trained_at(d.pop("trained_at", UNSET))

        model_version_out = cls(
            is_active=is_active,
            model_version=model_version,
            prediction_config_id=prediction_config_id,
            created_at=created_at,
            dataset_fingerprint=dataset_fingerprint,
            dataset_ids=dataset_ids,
            feature_names=feature_names,
            metrics=metrics,
            trained_at=trained_at,
        )

        model_version_out.additional_properties = d
        return model_version_out

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
