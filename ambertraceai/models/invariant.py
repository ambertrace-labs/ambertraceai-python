from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Invariant")


@_attrs_define
class Invariant:
    """A required-invariant declaration for a verified-profile platform.

    The manifest is the platform's machine-checked safety/liveness contract: the
    build-time gate and the (non-overridable) query-time proof both enforce it,
    so a verified answer provably satisfies every declared invariant.

        Attributes:
            assumed_absent (list[str] | None | Unset): forbid only: atoms treated as absent from the adversary's fact base
                (normally includes ``target`` itself).
            given (list[str] | None | Unset): require only: witness-base atoms assumed true when checking that ``target``
                derives.
            kind (str | Unset): Invariant kind. 'forbid' (safety): ``target`` must NOT be derivable from any admissible fact
                base — bars a forbidden grant however rules are authored. 'require' (liveness): from the witness base ``given``
                (all true), ``target`` MUST derive — catches a needed safety rule being suppressed. Default: 'forbid'.
            name (None | str | Unset): Human-readable invariant name; appears in violation messages.
            target (None | str | Unset): The atom/derived field this invariant constrains (e.g. 'permit_delete').
    """

    assumed_absent: list[str] | None | Unset = UNSET
    given: list[str] | None | Unset = UNSET
    kind: str | Unset = "forbid"
    name: None | str | Unset = UNSET
    target: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        assumed_absent: list[str] | None | Unset
        if isinstance(self.assumed_absent, Unset):
            assumed_absent = UNSET
        elif isinstance(self.assumed_absent, list):
            assumed_absent = self.assumed_absent

        else:
            assumed_absent = self.assumed_absent

        given: list[str] | None | Unset
        if isinstance(self.given, Unset):
            given = UNSET
        elif isinstance(self.given, list):
            given = self.given

        else:
            given = self.given

        kind = self.kind

        name: None | str | Unset
        if isinstance(self.name, Unset):
            name = UNSET
        else:
            name = self.name

        target: None | str | Unset
        if isinstance(self.target, Unset):
            target = UNSET
        else:
            target = self.target

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if assumed_absent is not UNSET:
            field_dict["assumed_absent"] = assumed_absent
        if given is not UNSET:
            field_dict["given"] = given
        if kind is not UNSET:
            field_dict["kind"] = kind
        if name is not UNSET:
            field_dict["name"] = name
        if target is not UNSET:
            field_dict["target"] = target

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)

        def _parse_assumed_absent(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                assumed_absent_type_0 = cast(list[str], data)

                return assumed_absent_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        assumed_absent = _parse_assumed_absent(d.pop("assumed_absent", UNSET))

        def _parse_given(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                given_type_0 = cast(list[str], data)

                return given_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        given = _parse_given(d.pop("given", UNSET))

        kind = d.pop("kind", UNSET)

        def _parse_name(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        name = _parse_name(d.pop("name", UNSET))

        def _parse_target(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        target = _parse_target(d.pop("target", UNSET))

        invariant = cls(
            assumed_absent=assumed_absent,
            given=given,
            kind=kind,
            name=name,
            target=target,
        )

        invariant.additional_properties = d
        return invariant

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
