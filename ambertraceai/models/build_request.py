from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.build_request_config import BuildRequestConfig
    from ..models.build_request_scored_determinations_type_0 import (
        BuildRequestScoredDeterminationsType0,
    )
    from ..models.invariant import Invariant


T = TypeVar("T", bound="BuildRequest")


@_attrs_define
class BuildRequest:
    """
    Attributes:
        domain_id (int):
        config (BuildRequestConfig | Unset):
        invariant_manifest (list[Invariant] | None | Unset): Verified profile only. The required-invariant manifest — a
            list of forbid/require obligations enforced at build and on every query. See the Invariant schema.
        override_verification_gate (bool | Unset): Human-in-the-loop override. If the build-time verification gate is
            violated and this is True, the build does NOT fail — instead the platform is built as a STANDARD (non-verified)
            platform and the violations are recorded in ``config.verification_gate_violations``. The verified label is
            reserved for rule sets that pass the gate. The query-time proof is never overridable, so this can never produce
            an unsound ``proof_checked`` certificate. Default: False.
        scored_determinations (BuildRequestScoredDeterminationsType0 | None | Unset): Verified profile only. Score an
            OPEN-TEXTURED predicate that bright-line rules cannot decide (e.g. compatibility, reasonableness, materiality,
            good-faith). When enabled, at query time the platform's own language model is given the predicate's doctrine
            plus the named request text fields and returns a calibrated probability that the predicate holds; that
            probability is admitted as a confidence-carrying fact subject to τ (``verified_min_confidence``) — at or above τ
            it can support a permit, below τ (or if the model abstains, is out of distribution, or disagrees with itself) it
            admits no fact and the request routes to an escalate rule instead. The score is computed on the server from the
            text (a caller cannot set it). Shape: ``{"enabled": bool, "determinations": [{"head": str, "question": str,
            "doctrine": str, "situation_fields": {label: request_field}}]}``. Its guarantee is empirical (calibration-in-
            regime + coherent input + fail-closed on out-of-distribution input) — weaker than the exact deductive proofs;
            use it only where deduction is silent.
        team_id (int | None | Unset): Required when visibility='team'; the caller must be a member.
        verified_min_confidence (float | None | Unset): Verified profile only. τ — the certified-fact confidence
            threshold in [0,1]. Facts (from retrieval or extracted from the query text) below τ are rejected at the
            neural→symbolic boundary and surfaced in ``explanation.rejected_facts`` rather than silently used.
        verified_profile (bool | Unset): Build in the verified profile. Verified platforms gate facts by a confidence
            threshold (τ) and return a proof certificate on every query (see ``proof_checked``). The rule set must be valid
            and satisfy ``invariant_manifest`` or the build fails (see ``override_verification_gate``). Default: False.
        visibility (None | str | Unset): Sharing audience: 'user' (private, default) | 'team' | 'org'.
    """

    domain_id: int
    config: BuildRequestConfig | Unset = UNSET
    invariant_manifest: list[Invariant] | None | Unset = UNSET
    override_verification_gate: bool | Unset = False
    scored_determinations: BuildRequestScoredDeterminationsType0 | None | Unset = UNSET
    team_id: int | None | Unset = UNSET
    verified_min_confidence: float | None | Unset = UNSET
    verified_profile: bool | Unset = False
    visibility: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.build_request_scored_determinations_type_0 import (
            BuildRequestScoredDeterminationsType0,
        )

        domain_id = self.domain_id

        config: dict[str, Any] | Unset = UNSET
        if not isinstance(self.config, Unset):
            config = self.config.to_dict()

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

        override_verification_gate = self.override_verification_gate

        scored_determinations: dict[str, Any] | None | Unset
        if isinstance(self.scored_determinations, Unset):
            scored_determinations = UNSET
        elif isinstance(
            self.scored_determinations, BuildRequestScoredDeterminationsType0
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

        verified_profile = self.verified_profile

        visibility: None | str | Unset
        if isinstance(self.visibility, Unset):
            visibility = UNSET
        else:
            visibility = self.visibility

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "domain_id": domain_id,
            }
        )
        if config is not UNSET:
            field_dict["config"] = config
        if invariant_manifest is not UNSET:
            field_dict["invariant_manifest"] = invariant_manifest
        if override_verification_gate is not UNSET:
            field_dict["override_verification_gate"] = override_verification_gate
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
        from ..models.build_request_config import BuildRequestConfig
        from ..models.build_request_scored_determinations_type_0 import (
            BuildRequestScoredDeterminationsType0,
        )
        from ..models.invariant import Invariant

        d = dict(src_dict)
        domain_id = d.pop("domain_id")

        _config = d.pop("config", UNSET)
        config: BuildRequestConfig | Unset
        if isinstance(_config, Unset):
            config = UNSET
        else:
            config = BuildRequestConfig.from_dict(_config)

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

        override_verification_gate = d.pop("override_verification_gate", UNSET)

        def _parse_scored_determinations(
            data: object,
        ) -> BuildRequestScoredDeterminationsType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                scored_determinations_type_0 = (
                    BuildRequestScoredDeterminationsType0.from_dict(data)
                )

                return scored_determinations_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(BuildRequestScoredDeterminationsType0 | None | Unset, data)

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

        verified_profile = d.pop("verified_profile", UNSET)

        def _parse_visibility(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        visibility = _parse_visibility(d.pop("visibility", UNSET))

        build_request = cls(
            domain_id=domain_id,
            config=config,
            invariant_manifest=invariant_manifest,
            override_verification_gate=override_verification_gate,
            scored_determinations=scored_determinations,
            team_id=team_id,
            verified_min_confidence=verified_min_confidence,
            verified_profile=verified_profile,
            visibility=visibility,
        )

        build_request.additional_properties = d
        return build_request

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
