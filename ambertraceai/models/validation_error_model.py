from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.validation_error_model_ctx_type_0 import ValidationErrorModelCtxType0


T = TypeVar("T", bound="ValidationErrorModel")


@_attrs_define
class ValidationErrorModel:
    """
    Attributes:
        ctx (None | Unset | ValidationErrorModelCtxType0): an optional object which contains values required to render
            the error message.
        loc (list[str] | None | Unset): the error's location as a list.
        msg (None | str | Unset): a computer-readable identifier of the error type.
        type_ (None | str | Unset): a human readable explanation of the error.
    """

    ctx: None | Unset | ValidationErrorModelCtxType0 = UNSET
    loc: list[str] | None | Unset = UNSET
    msg: None | str | Unset = UNSET
    type_: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.validation_error_model_ctx_type_0 import (
            ValidationErrorModelCtxType0,
        )

        ctx: dict[str, Any] | None | Unset
        if isinstance(self.ctx, Unset):
            ctx = UNSET
        elif isinstance(self.ctx, ValidationErrorModelCtxType0):
            ctx = self.ctx.to_dict()
        else:
            ctx = self.ctx

        loc: list[str] | None | Unset
        if isinstance(self.loc, Unset):
            loc = UNSET
        elif isinstance(self.loc, list):
            loc = self.loc

        else:
            loc = self.loc

        msg: None | str | Unset
        if isinstance(self.msg, Unset):
            msg = UNSET
        else:
            msg = self.msg

        type_: None | str | Unset
        if isinstance(self.type_, Unset):
            type_ = UNSET
        else:
            type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if ctx is not UNSET:
            field_dict["ctx"] = ctx
        if loc is not UNSET:
            field_dict["loc"] = loc
        if msg is not UNSET:
            field_dict["msg"] = msg
        if type_ is not UNSET:
            field_dict["type_"] = type_

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.validation_error_model_ctx_type_0 import (
            ValidationErrorModelCtxType0,
        )

        d = dict(src_dict)

        def _parse_ctx(data: object) -> None | Unset | ValidationErrorModelCtxType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ctx_type_0 = ValidationErrorModelCtxType0.from_dict(data)

                return ctx_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | ValidationErrorModelCtxType0, data)

        ctx = _parse_ctx(d.pop("ctx", UNSET))

        def _parse_loc(data: object) -> list[str] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                loc_type_0 = cast(list[str], data)

                return loc_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[str] | None | Unset, data)

        loc = _parse_loc(d.pop("loc", UNSET))

        def _parse_msg(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        msg = _parse_msg(d.pop("msg", UNSET))

        def _parse_type_(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        type_ = _parse_type_(d.pop("type_", UNSET))

        validation_error_model = cls(
            ctx=ctx,
            loc=loc,
            msg=msg,
            type_=type_,
        )

        validation_error_model.additional_properties = d
        return validation_error_model

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
