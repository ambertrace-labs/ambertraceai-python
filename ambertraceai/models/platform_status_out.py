from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.platform_status_out_decision_vocabulary_type_0 import PlatformStatusOutDecisionVocabularyType0


T = TypeVar("T", bound="PlatformStatusOut")


@_attrs_define
class PlatformStatusOut:
    """
    Attributes:
        name (str):
        platform_id (int):
        status (str):
        decision_vocabulary (None | PlatformStatusOutDecisionVocabularyType0 | Unset): The platform's declared terminal
            decision verbs ({'verbs': [{verb, rank, restrictive, default, label}, ...]}), minted from the policy text at
            build. Null when the policy declares no custom verbs.
        version (int | Unset):  Default: 1.
    """

    name: str
    platform_id: int
    status: str
    decision_vocabulary: None | PlatformStatusOutDecisionVocabularyType0 | Unset = UNSET
    version: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.platform_status_out_decision_vocabulary_type_0 import PlatformStatusOutDecisionVocabularyType0

        name = self.name

        platform_id = self.platform_id

        status = self.status

        decision_vocabulary: dict[str, Any] | None | Unset
        if isinstance(self.decision_vocabulary, Unset):
            decision_vocabulary = UNSET
        elif isinstance(self.decision_vocabulary, PlatformStatusOutDecisionVocabularyType0):
            decision_vocabulary = self.decision_vocabulary.to_dict()
        else:
            decision_vocabulary = self.decision_vocabulary

        version = self.version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "platform_id": platform_id,
                "status": status,
            }
        )
        if decision_vocabulary is not UNSET:
            field_dict["decision_vocabulary"] = decision_vocabulary
        if version is not UNSET:
            field_dict["version"] = version

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.platform_status_out_decision_vocabulary_type_0 import PlatformStatusOutDecisionVocabularyType0

        d = dict(src_dict)
        name = d.pop("name")

        platform_id = d.pop("platform_id")

        status = d.pop("status")

        def _parse_decision_vocabulary(data: object) -> None | PlatformStatusOutDecisionVocabularyType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                decision_vocabulary_type_0 = PlatformStatusOutDecisionVocabularyType0.from_dict(data)

                return decision_vocabulary_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | PlatformStatusOutDecisionVocabularyType0 | Unset, data)

        decision_vocabulary = _parse_decision_vocabulary(d.pop("decision_vocabulary", UNSET))

        version = d.pop("version", UNSET)

        platform_status_out = cls(
            name=name,
            platform_id=platform_id,
            status=status,
            decision_vocabulary=decision_vocabulary,
            version=version,
        )

        platform_status_out.additional_properties = d
        return platform_status_out

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
