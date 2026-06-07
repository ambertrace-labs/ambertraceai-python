from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.obligation_suggestion import ObligationSuggestion


T = TypeVar("T", bound="ObligationSuggestionsOut")


@_attrs_define
class ObligationSuggestionsOut:
    """Suggested require-obligations for a platform's active verified rules.

    Attributes:
        platform_id (int):
        suggestions (list[ObligationSuggestion] | Unset):
    """

    platform_id: int
    suggestions: list[ObligationSuggestion] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        platform_id = self.platform_id

        suggestions: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.suggestions, Unset):
            suggestions = []
            for suggestions_item_data in self.suggestions:
                suggestions_item = suggestions_item_data.to_dict()
                suggestions.append(suggestions_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "platform_id": platform_id,
            }
        )
        if suggestions is not UNSET:
            field_dict["suggestions"] = suggestions

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.obligation_suggestion import ObligationSuggestion

        d = dict(src_dict)
        platform_id = d.pop("platform_id")

        _suggestions = d.pop("suggestions", UNSET)
        suggestions: list[ObligationSuggestion] | Unset = UNSET
        if _suggestions is not UNSET:
            suggestions = []
            for suggestions_item_data in _suggestions:
                suggestions_item = ObligationSuggestion.from_dict(suggestions_item_data)

                suggestions.append(suggestions_item)

        obligation_suggestions_out = cls(
            platform_id=platform_id,
            suggestions=suggestions,
        )

        obligation_suggestions_out.additional_properties = d
        return obligation_suggestions_out

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
