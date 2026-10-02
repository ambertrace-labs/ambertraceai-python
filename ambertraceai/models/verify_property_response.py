from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.verify_property_response_witness_recertification_type_0 import (
        VerifyPropertyResponseWitnessRecertificationType0,
    )
    from ..models.verify_property_response_witness_type_0 import VerifyPropertyResponseWitnessType0
    from ..models.verify_property_search import VerifyPropertySearch


T = TypeVar("T", bound="VerifyPropertyResponse")


@_attrs_define
class VerifyPropertyResponse:
    """Certified verdict of a universal claim: HOLDS (exhaustive), VIOLATED (certified
    counterexample) or ABSTAIN (no verdict). `result`, `proof_summary`, `certified`,
    `proof_checked` and `search` are all computed from ONE source -- the proven
    checker's decision -- and always name the same verdict.

        Attributes:
            proof_checked (bool): The AUTHORITATIVE field: true iff the verdict was decided by the proven checker (HOLDS) /
                the witness re-certified (VIOLATED); always false on ABSTAIN.
            proof_summary (str): Fixed-template rendering of the fields above; never free text.
            result (str): HOLDS | VIOLATED | ABSTAIN.
            search (VerifyPropertySearch):
            certified (None | str | Unset): 'exhaustive' (HOLDS) | 'witness' (VIOLATED) | null (ABSTAIN).
            reason (None | str | Unset): ABSTAIN only: why no verdict was reached (e.g. over_bound, over_ceiling, timeout,
                unsupported_mechanism).
            witness (None | Unset | VerifyPropertyResponseWitnessType0): Present iff VIOLATED: the counterexample member
                (every agent's true type, the deviating `agent` and its `misreport`), re-certified through the trusted kernel.
            witness_index (int | None | Unset): VIOLATED only: 0-based position of the witness in the fixed enumeration
                order (first variable slowest).
            witness_recertification (None | Unset | VerifyPropertyResponseWitnessRecertificationType0): VIOLATED (or a
                failed re-certification): the two kernel derivations behind the witness -- truthful vs deviated reports and
                outcomes, and which checker ratified them.
    """

    proof_checked: bool
    proof_summary: str
    result: str
    search: VerifyPropertySearch
    certified: None | str | Unset = UNSET
    reason: None | str | Unset = UNSET
    witness: None | Unset | VerifyPropertyResponseWitnessType0 = UNSET
    witness_index: int | None | Unset = UNSET
    witness_recertification: None | Unset | VerifyPropertyResponseWitnessRecertificationType0 = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.verify_property_response_witness_recertification_type_0 import (
            VerifyPropertyResponseWitnessRecertificationType0,
        )
        from ..models.verify_property_response_witness_type_0 import VerifyPropertyResponseWitnessType0

        proof_checked = self.proof_checked

        proof_summary = self.proof_summary

        result = self.result

        search = self.search.to_dict()

        certified: None | str | Unset
        if isinstance(self.certified, Unset):
            certified = UNSET
        else:
            certified = self.certified

        reason: None | str | Unset
        if isinstance(self.reason, Unset):
            reason = UNSET
        else:
            reason = self.reason

        witness: dict[str, Any] | None | Unset
        if isinstance(self.witness, Unset):
            witness = UNSET
        elif isinstance(self.witness, VerifyPropertyResponseWitnessType0):
            witness = self.witness.to_dict()
        else:
            witness = self.witness

        witness_index: int | None | Unset
        if isinstance(self.witness_index, Unset):
            witness_index = UNSET
        else:
            witness_index = self.witness_index

        witness_recertification: dict[str, Any] | None | Unset
        if isinstance(self.witness_recertification, Unset):
            witness_recertification = UNSET
        elif isinstance(self.witness_recertification, VerifyPropertyResponseWitnessRecertificationType0):
            witness_recertification = self.witness_recertification.to_dict()
        else:
            witness_recertification = self.witness_recertification

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "proof_checked": proof_checked,
                "proof_summary": proof_summary,
                "result": result,
                "search": search,
            }
        )
        if certified is not UNSET:
            field_dict["certified"] = certified
        if reason is not UNSET:
            field_dict["reason"] = reason
        if witness is not UNSET:
            field_dict["witness"] = witness
        if witness_index is not UNSET:
            field_dict["witness_index"] = witness_index
        if witness_recertification is not UNSET:
            field_dict["witness_recertification"] = witness_recertification

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.verify_property_response_witness_recertification_type_0 import (
            VerifyPropertyResponseWitnessRecertificationType0,
        )
        from ..models.verify_property_response_witness_type_0 import VerifyPropertyResponseWitnessType0
        from ..models.verify_property_search import VerifyPropertySearch

        d = dict(src_dict)
        proof_checked = d.pop("proof_checked")

        proof_summary = d.pop("proof_summary")

        result = d.pop("result")

        search = VerifyPropertySearch.from_dict(d.pop("search"))

        def _parse_certified(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        certified = _parse_certified(d.pop("certified", UNSET))

        def _parse_reason(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        reason = _parse_reason(d.pop("reason", UNSET))

        def _parse_witness(data: object) -> None | Unset | VerifyPropertyResponseWitnessType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                witness_type_0 = VerifyPropertyResponseWitnessType0.from_dict(data)

                return witness_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VerifyPropertyResponseWitnessType0, data)

        witness = _parse_witness(d.pop("witness", UNSET))

        def _parse_witness_index(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        witness_index = _parse_witness_index(d.pop("witness_index", UNSET))

        def _parse_witness_recertification(
            data: object,
        ) -> None | Unset | VerifyPropertyResponseWitnessRecertificationType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                witness_recertification_type_0 = VerifyPropertyResponseWitnessRecertificationType0.from_dict(data)

                return witness_recertification_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VerifyPropertyResponseWitnessRecertificationType0, data)

        witness_recertification = _parse_witness_recertification(d.pop("witness_recertification", UNSET))

        verify_property_response = cls(
            proof_checked=proof_checked,
            proof_summary=proof_summary,
            result=result,
            search=search,
            certified=certified,
            reason=reason,
            witness=witness,
            witness_index=witness_index,
            witness_recertification=witness_recertification,
        )

        verify_property_response.additional_properties = d
        return verify_property_response

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
