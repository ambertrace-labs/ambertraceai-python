from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.invariant import Invariant
    from ..models.platform_update_request_scored_determinations_type_0 import (
        PlatformUpdateRequestScoredDeterminationsType0,
    )


T = TypeVar("T", bound="PlatformUpdateRequest")


@_attrs_define
class PlatformUpdateRequest:
    """Mutable verified-profile settings for an existing platform (C1a/C1c).

    All fields optional — only those provided are applied. Flipping
    ``verified_profile`` to ``True`` triggers a safe-flip validation of the
    platform's existing active rules (see ``BuilderService.update_platform``).

        Attributes:
            invariant_manifest (list[Invariant] | None | Unset): Replace the platform's required-invariant manifest (see the
                Invariant schema).
            scored_determinations (None | PlatformUpdateRequestScoredDeterminationsType0 | Unset): Set or replace the open-
                textured scored determinations (verified profile only). See the same field on the build request for the shape
                and semantics — a server-computed calibrated probability for a judgment predicate, admitted as a confidence-
                carrying fact subject to τ; at or above τ it can support a permit, otherwise the request routes to escalate
                (deductive-first, fail-closed).
            team_id (int | None | Unset): Required when visibility='team'; the caller must be a member.
            verified_min_confidence (float | None | Unset): Update the certified-fact confidence threshold τ in [0,1].
            verified_profile (bool | None | Unset): Enable/disable the verified profile on an existing platform. Enabling
                re-validates every active rule; if any are not verified-profile-safe the flip is rejected with HTTP 409 listing
                the offending rules.
            visibility (None | str | Unset): Re-share audience: 'user' (private) | 'team' | 'org'. Only the owner/org-admin
                may change it.
    """

    invariant_manifest: list[Invariant] | None | Unset = UNSET
    scored_determinations: (
        None | PlatformUpdateRequestScoredDeterminationsType0 | Unset
    ) = UNSET
    team_id: int | None | Unset = UNSET
    verified_min_confidence: float | None | Unset = UNSET
    verified_profile: bool | None | Unset = UNSET
    visibility: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.platform_update_request_scored_determinations_type_0 import (
            PlatformUpdateRequestScoredDeterminationsType0,
        )

        invariant_manifest: list[dict[str, Any]] | None | Unset
        if isinstance(self.invariant_manifest, Unset):
            invariant_manifest = UNSET
        elif isinstance(self.invariant_manifest, list):
            invariant_manifest = []
            for invariant_manifest_type_0_item_data in self.invariant_manifest:
                invariant_manifest_type_0_item = (
                    invariant_manifest_type_0_item_data.to_dict()
                )
                invariant_manifest.append(invariant_manifest_type_0_item)

        else:
            invariant_manifest = self.invariant_manifest

        scored_determinations: dict[str, Any] | None | Unset
        if isinstance(self.scored_determinations, Unset):
            scored_determinations = UNSET
        elif isinstance(
            self.scored_determinations, PlatformUpdateRequestScoredDeterminationsType0
        ):
            scored_determinations = self.scored_determinations.to_dict()
        else:
            scored_determinations = self.scored_determinations

        team_id: int | None | Unset
        if isinstance(self.team_id, Unset):
            team_id = UNSET
        else:
            team_id = self.team_id

        verified_min_confidence: float | None | Unset
        if isinstance(self.verified_min_confidence, Unset):
            verified_min_confidence = UNSET
        else:
            verified_min_confidence = self.verified_min_confidence

        verified_profile: bool | None | Unset
        if isinstance(self.verified_profile, Unset):
            verified_profile = UNSET
        else:
            verified_profile = self.verified_profile

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        else:
            visibility = self.visibility

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if invariant_manifest is not UNSET:
            field_dict["invariant_manifest"] = invariant_manifest
        if scored_determinations is not UNSET:
            field_dict["scored_determinations"] = scored_determinations
        if team_id is not UNSET:
            field_dict["team_id"] = team_id
        if verified_min_confidence is not UNSET:
            field_dict["verified_min_confidence"] = verified_min_confidence
        if verified_profile is not UNSET:
            field_dict["verified_profile"] = verified_profile
        if visibility is not UNSET:
            field_dict["visibility"] = visibility

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.invariant import Invariant
        from ..models.platform_update_request_scored_determinations_type_0 import (
            PlatformUpdateRequestScoredDeterminationsType0,
        )

        d = dict(src_dict)

        def _parse_invariant_manifest(data: object) -> list[Invariant] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                invariant_manifest_type_0 = []
                _invariant_manifest_type_0 = data
                for invariant_manifest_type_0_item_data in _invariant_manifest_type_0:
                    invariant_manifest_type_0_item = Invariant.from_dict(
                        invariant_manifest_type_0_item_data
                    )

                    invariant_manifest_type_0.append(invariant_manifest_type_0_item)

                return invariant_manifest_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[Invariant] | None | Unset, data)

        invariant_manifest = _parse_invariant_manifest(
            d.pop("invariant_manifest", UNSET)
        )

        def _parse_scored_determinations(
            data: object,
        ) -> None | PlatformUpdateRequestScoredDeterminationsType0 | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scored_determinations_type_0 = (
                    PlatformUpdateRequestScoredDeterminationsType0.from_dict(data)
                )

                return scored_determinations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(
                None | PlatformUpdateRequestScoredDeterminationsType0 | Unset, data
            )

        scored_determinations = _parse_scored_determinations(
            d.pop("scored_determinations", UNSET)
        )

        def _parse_team_id(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        team_id = _parse_team_id(d.pop("team_id", UNSET))

        def _parse_verified_min_confidence(data: object) -> float | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(float | None | Unset, data)

        verified_min_confidence = _parse_verified_min_confidence(
            d.pop("verified_min_confidence", UNSET)
        )

        def _parse_verified_profile(data: object) -> bool | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(bool | None | Unset, data)

        verified_profile = _parse_verified_profile(d.pop("verified_profile", UNSET))

        def _parse_visibility(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))

        platform_update_request = cls(
            invariant_manifest=invariant_manifest,
            scored_determinations=scored_determinations,
            team_id=team_id,
            verified_min_confidence=verified_min_confidence,
            verified_profile=verified_profile,
            visibility=visibility,
        )

        platform_update_request.additional_properties = d
        return platform_update_request

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
