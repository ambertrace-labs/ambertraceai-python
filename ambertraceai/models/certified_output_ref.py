from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.certified_output_ref_source_type import CertifiedOutputRefSourceType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CertifiedOutputRef")


@_attrs_define
class CertifiedOutputRef:
    """A payoff parameter taken from a CERTIFIED platform output instead of a number you
    type: the server fetches the referenced record in your organisation, requires its
    proof_checked marker, extracts `field` and resolves `round(value * mul + add)`.

        Attributes:
            field (str): Whitelisted dot-path (see source_type).
            source_id (int): Prediction record id, or verify_property job id.
            source_type (CertifiedOutputRefSourceType): 'prediction': a persisted prediction record (fields value,
                probability, interval.lower, interval.upper). 'verify_property': a completed, proof_checked verify_property job
                (fields search.space_size, witness_index, witness_recertification.agent_gain,
                witness_recertification.truthful_payoffs.N / deviated_payoffs.N).
            add (int | Unset): Integer offset (default 0). Default: 0.
            mul (int | Unset): Integer multiplier (default 1). Default: 1.
    """

    field: str
    source_id: int
    source_type: CertifiedOutputRefSourceType
    add: int | Unset = 0
    mul: int | Unset = 1
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field = self.field

        source_id = self.source_id

        source_type = self.source_type.value

        add = self.add

        mul = self.mul

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "field": field,
                "source_id": source_id,
                "source_type": source_type,
            }
        )
        if add is not UNSET:
            field_dict["add"] = add
        if mul is not UNSET:
            field_dict["mul"] = mul

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        field = d.pop("field")

        source_id = d.pop("source_id")

        source_type = CertifiedOutputRefSourceType(d.pop("source_type"))

        add = d.pop("add", UNSET)

        mul = d.pop("mul", UNSET)

        certified_output_ref = cls(
            field=field,
            source_id=source_id,
            source_type=source_type,
            add=add,
            mul=mul,
        )

        certified_output_ref.additional_properties = d
        return certified_output_ref

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
