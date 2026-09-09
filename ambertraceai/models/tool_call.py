from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tool_call_args import ToolCallArgs


T = TypeVar("T", bound="ToolCall")


@_attrs_define
class ToolCall:
    """
    Attributes:
        tool (str): Tool / action name the agent proposes
        args (ToolCallArgs | Unset): Structured tool arguments. Mapped (by canonical field name) directly to
            client_facts — NO LLM extraction; the request IS the facts. Keys matching a declared policy field are gated;
            unknown keys are rejected-and-surfaced by the certified-fact gate. Each value may be a bare scalar OR a
            ``{"value": <v>, "confidence": <c>}`` carrier for per-observation confidence; on a ``require_confidence``
            platform every value MUST be a carrier.
    """

    tool: str
    args: ToolCallArgs | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool = self.tool

        args: dict[str, Any] | Unset = UNSET
        if not isinstance(self.args, Unset):
            args = self.args.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "tool": tool,
            }
        )
        if args is not UNSET:
            field_dict["args"] = args

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.tool_call_args import ToolCallArgs

        d = dict(src_dict)
        tool = d.pop("tool")

        _args = d.pop("args", UNSET)
        args: ToolCallArgs | Unset
        if isinstance(_args, Unset):
            args = UNSET
        else:
            args = ToolCallArgs.from_dict(_args)

        tool_call = cls(
            tool=tool,
            args=args,
        )

        tool_call.additional_properties = d
        return tool_call

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
