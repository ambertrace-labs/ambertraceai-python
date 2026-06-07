from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.given_atom import GivenAtom


T = TypeVar("T", bound="Invariant")


@_attrs_define
class Invariant:
    """A required-invariant declaration for a verified-profile platform.

    The manifest is the platform's safety/liveness contract enforced at
    build time and on every query, so a verified answer provably satisfies
    every declared invariant.

    Atom vocabulary. An invariant ``target`` (and every entry in
    ``assumed_absent``) is a **boolean atom name**: a derived-fact field (a
    ``derive`` rule head, e.g. ``permit_delete``, ``deny_access``) or an input
    fact name.

    ``forbid`` reasons over *derivability* and is **value- and
    comparison-blind** (a deliberate, machine-checked soundness boundary): you
    cannot write "forbid ``approve`` when ``applicant_age < 18``" — the
    analyzer treats every non-forbidden atom as a freely externally-suppliable
    input, so a value-gated outcome is always reported derivable (conservative
    — never falsely "safe").

    ``require`` witnesses are **concrete**: each ``given`` entry is either a
    bare atom name (witness value ``True`` — use for boolean classification
    atoms) or a value-bound ``{"field": ..., "value": ...}`` object, so the
    obligation can witness real classifiers (conjunctions, set membership,
    numeric thresholds) and conclusion atoms reached through multiple rule
    hops. The safety pattern:

        # rules (engine, query time)
        derive is_trusted_device if device_managed and device_posture_score >= 70
        derive deny_access       if is_restricted_zone and not is_trusted_device
        # invariant (manifest gate): the deny conclusion must derive from THIS
        # concrete witness — catches A2 rule suppression anywhere in the chain.
        {"name": "untrusted device into restricted zone must deny",
         "kind": "require", "target": "deny_access",
         "given": [{"field": "target_zone", "value": "ot_network"},
                   {"field": "device_managed", "value": false}]}

    See ``docs/aria-design.md`` §2 and ``docs/aria-witness-value-binding.md``.

        Attributes:
            assumed_absent (list[str] | None | Unset): forbid only: boolean atoms treated as absent from every admissible
                fact base (normally includes ``target`` itself).
            given (list[GivenAtom | str] | None | Unset): require only: the concrete witness base from which ``target`` must
                derive. Each entry is a bare atom name (witness value True — use for boolean classification atoms like
                'is_underage') or a value-bound {'field', 'value'} object (use to witness numeric / enum / set classifiers, e.g.
                {'field': 'device_posture_score', 'value': 85}). A field may appear at most once.
            kind (str | Unset): Invariant kind. 'forbid' (safety): the boolean ``target`` atom must never be derivable —
                prevents a forbidden outcome regardless of how rules are authored; value-/comparison-blind by design. 'require'
                (liveness): from the concrete witness base ``given`` (bare atom names ⇒ True; {'field','value'} objects bind
                real scalars), the ``target`` must be derivable — ensures a required safety conclusion, possibly several rule
                hops deep, is maintained (see schema docstring + docs/aria-design.md §2). Default: 'forbid'.
            name (None | str | Unset): Human-readable invariant name; appears in violation messages.
            target (None | str | Unset): The boolean atom / derived field this invariant constrains (e.g. 'permit_delete',
                'block_approval'). Not a value test — see schema docstring for the value-gated pattern.
    """

    assumed_absent: list[str] | None | Unset = UNSET
    given: list[GivenAtom | str] | None | Unset = UNSET
    kind: str | Unset = "forbid"
    name: None | str | Unset = UNSET
    target: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.given_atom import GivenAtom

        assumed_absent: list[str] | None | Unset
        if isinstance(self.assumed_absent, Unset):
            assumed_absent = UNSET
        elif isinstance(self.assumed_absent, list):
            assumed_absent = self.assumed_absent

        else:
            assumed_absent = self.assumed_absent

        given: list[dict[str, Any] | str] | None | Unset
        if isinstance(self.given, Unset):
            given = UNSET
        elif isinstance(self.given, list):
            given = []
            for given_type_0_item_data in self.given:
                given_type_0_item: dict[str, Any] | str
                if isinstance(given_type_0_item_data, GivenAtom):
                    given_type_0_item = given_type_0_item_data.to_dict()
                else:
                    given_type_0_item = given_type_0_item_data
                given.append(given_type_0_item)

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
        from ..models.given_atom import GivenAtom

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

        def _parse_given(data: object) -> list[GivenAtom | str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                given_type_0 = []
                _given_type_0 = data
                for given_type_0_item_data in _given_type_0:

                    def _parse_given_type_0_item(data: object) -> GivenAtom | str:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            given_type_0_item_type_1 = GivenAtom.from_dict(data)

                            return given_type_0_item_type_1
                        except (TypeError, ValueError, AttributeError, KeyError):
                            pass
                        return cast(GivenAtom | str, data)

                    given_type_0_item = _parse_given_type_0_item(given_type_0_item_data)

                    given_type_0.append(given_type_0_item)

                return given_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[GivenAtom | str] | None | Unset, data)

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
