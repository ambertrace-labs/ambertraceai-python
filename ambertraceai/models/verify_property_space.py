from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VerifyPropertySpace")


@_attrs_define
class VerifyPropertySpace:
    """The finite space a ``verify_property`` claim quantifies over (v1 grammar).

    The space is the PRODUCT of every agent's type domain x which agent deviates x
    that agent's misreport domain; ``|S|`` is recomputed by the proven checker.

        Attributes:
            agents (int): Number of agents (voters / bidders); the v1 library supports 1 to 8.
            bound (int): REQUIRED finiteness bound: the largest |S| you accept. A space larger than `bound` (or than the
                platform ceiling) is an explicit ABSTAIN, never a partial answer.
            domain (list[int | str]): The finite value domain. plurality / majority: the alternatives (alphanumeric names,
                e.g. ['A','B','C']); vickrey / first_price: the discrete bid grid (distinct non-negative integers, at most 10).
                At most 64 entries are accepted at all (the library's own caps are tighter).
            mechanism (str): Mechanism library entry: 'plurality' (3-5 alternatives, ties break in `domain` order),
                'majority' (exactly 2 alternatives, tie -> first), 'vickrey' (2 bidders, second-price) or 'first_price' (2
                bidders, first-price; a manipulable control).
    """

    agents: int
    bound: int
    domain: list[int | str]
    mechanism: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        agents = self.agents

        bound = self.bound

        domain = []
        for domain_item_data in self.domain:
            domain_item: int | str
            domain_item = domain_item_data
            domain.append(domain_item)

        mechanism = self.mechanism

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "agents": agents,
                "bound": bound,
                "domain": domain,
                "mechanism": mechanism,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        agents = d.pop("agents")

        bound = d.pop("bound")

        domain = []
        _domain = d.pop("domain")
        for domain_item_data in _domain:

            def _parse_domain_item(data: object) -> int | str:
                return cast(int | str, data)

            domain_item = _parse_domain_item(domain_item_data)

            domain.append(domain_item)

        mechanism = d.pop("mechanism")

        verify_property_space = cls(
            agents=agents,
            bound=bound,
            domain=domain,
            mechanism=mechanism,
        )

        verify_property_space.additional_properties = d
        return verify_property_space

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
