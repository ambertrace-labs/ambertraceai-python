from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.data_context_out_datasets_item import DataContextOutDatasetsItem
    from ..models.data_context_out_domain_type_0 import DataContextOutDomainType0
    from ..models.data_context_out_eval_config_type_0 import (
        DataContextOutEvalConfigType0,
    )


T = TypeVar("T", bound="DataContextOut")


@_attrs_define
class DataContextOut:
    """
    Attributes:
        datasets (list[DataContextOutDatasetsItem] | Unset):
        domain (DataContextOutDomainType0 | None | Unset):
        eval_config (DataContextOutEvalConfigType0 | None | Unset):
    """

    datasets: list[DataContextOutDatasetsItem] | Unset = UNSET
    domain: DataContextOutDomainType0 | None | Unset = UNSET
    eval_config: DataContextOutEvalConfigType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.data_context_out_domain_type_0 import DataContextOutDomainType0
        from ..models.data_context_out_eval_config_type_0 import (
            DataContextOutEvalConfigType0,
        )

        datasets: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.datasets, Unset):
            datasets = []
            for datasets_item_data in self.datasets:
                datasets_item = datasets_item_data.to_dict()
                datasets.append(datasets_item)

        domain: dict[str, Any] | None | Unset
        if isinstance(self.domain, Unset):
            domain = UNSET
        elif isinstance(self.domain, DataContextOutDomainType0):
            domain = self.domain.to_dict()
        else:
            domain = self.domain

        eval_config: dict[str, Any] | None | Unset
        if isinstance(self.eval_config, Unset):
            eval_config = UNSET
        elif isinstance(self.eval_config, DataContextOutEvalConfigType0):
            eval_config = self.eval_config.to_dict()
        else:
            eval_config = self.eval_config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if datasets is not UNSET:
            field_dict["datasets"] = datasets
        if domain is not UNSET:
            field_dict["domain"] = domain
        if eval_config is not UNSET:
            field_dict["eval_config"] = eval_config

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.data_context_out_datasets_item import DataContextOutDatasetsItem
        from ..models.data_context_out_domain_type_0 import DataContextOutDomainType0
        from ..models.data_context_out_eval_config_type_0 import (
            DataContextOutEvalConfigType0,
        )

        d = dict(src_dict)
        _datasets = d.pop("datasets", UNSET)
        datasets: list[DataContextOutDatasetsItem] | Unset = UNSET
        if _datasets is not UNSET:
            datasets = []
            for datasets_item_data in _datasets:
                datasets_item = DataContextOutDatasetsItem.from_dict(datasets_item_data)

                datasets.append(datasets_item)

        def _parse_domain(data: object) -> DataContextOutDomainType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                domain_type_0 = DataContextOutDomainType0.from_dict(data)

                return domain_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataContextOutDomainType0 | None | Unset, data)

        domain = _parse_domain(d.pop("domain", UNSET))

        def _parse_eval_config(
            data: object,
        ) -> DataContextOutEvalConfigType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                eval_config_type_0 = DataContextOutEvalConfigType0.from_dict(data)

                return eval_config_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(DataContextOutEvalConfigType0 | None | Unset, data)

        eval_config = _parse_eval_config(d.pop("eval_config", UNSET))

        data_context_out = cls(
            datasets=datasets,
            domain=domain,
            eval_config=eval_config,
        )

        data_context_out.additional_properties = d
        return data_context_out

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
