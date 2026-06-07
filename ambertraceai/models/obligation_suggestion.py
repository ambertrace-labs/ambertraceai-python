from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.given_atom import GivenAtom


T = TypeVar("T", bound="ObligationSuggestion")


@_attrs_define
class ObligationSuggestion:
    """A suggested ``require`` invariant for a verified platform (ARIA WP5).

    One per active verified ``derive`` rule that has no guarding obligation.
    Adding it to the manifest makes that rule's suppression detectable at the
    build/query gate (threat-model A2). Suggestions are advisory — never
    auto-applied; the author reviews and adds via PATCH /platforms/{id}.

        Attributes:
            target (str):
            given (list[GivenAtom | str] | Unset):
            kind (str | Unset):  Default: 'require'.
            name (None | str | Unset):
            rationale (None | str | Unset):
    """

    target: str
    given: list[GivenAtom | str] | Unset = UNSET
    kind: str | Unset = "require"
    name: None | str | Unset = UNSET
    rationale: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.given_atom import GivenAtom

        target = self.target

        given: list[dict[str, Any] | str] | Unset = UNSET
        if not isinstance(self.given, Unset):
            given = []
            for given_item_data in self.given:
                given_item: dict[str, Any] | str
                if isinstance(given_item_data, GivenAtom):
                    given_item = given_item_data.to_dict()
                else:
                    given_item = given_item_data
                given.append(given_item)

        kind = self.kind

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        rationale: None | str | Unset
        if isinstance(self.rationale, Unset):
            rationale = UNSET
        else:
            rationale = self.rationale

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "target": target,
            }
        )
        if given is not UNSET:
            field_dict["given"] = given
        if kind is not UNSET:
            field_dict["kind"] = kind
        if name is not UNSET:
            field_dict["name"] = name
        if rationale is not UNSET:
            field_dict["rationale"] = rationale

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.given_atom import GivenAtom

        d = dict(src_dict)
        target = d.pop("target")

        _given = d.pop("given", UNSET)
        given: list[GivenAtom | str] | Unset = UNSET
        if _given is not UNSET:
            given = []
            for given_item_data in _given:

                def _parse_given_item(data: object) -> GivenAtom | str:
                    try:
                        if not isinstance(data, dict):
                            raise TypeError()
                        given_item_type_1 = GivenAtom.from_dict(data)

                        return given_item_type_1
                    except (TypeError, ValueError, AttributeError, KeyError):
                        pass
                    return cast(GivenAtom | str, data)

                given_item = _parse_given_item(given_item_data)

                given.append(given_item)

        kind = d.pop("kind", UNSET)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_rationale(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        rationale = _parse_rationale(d.pop("rationale", UNSET))

        obligation_suggestion = cls(
            target=target,
            given=given,
            kind=kind,
            name=name,
            rationale=rationale,
        )

        obligation_suggestion.additional_properties = d
        return obligation_suggestion

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
