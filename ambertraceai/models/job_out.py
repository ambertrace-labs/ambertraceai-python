from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_out_result_type_0 import JobOutResultType0


T = TypeVar("T", bound="JobOut")


@_attrs_define
class JobOut:
    """
    Attributes:
        id (int):
        status (str):
        type_ (str):
        created_at (None | str | Unset):
        error_message (None | str | Unset):
        progress (int | None | Unset):
        result (JobOutResultType0 | None | Unset):
        step (None | str | Unset):
        updated_at (None | str | Unset):
    """

    id: int
    status: str
    type_: str
    created_at: None | str | Unset = UNSET
    error_message: None | str | Unset = UNSET
    progress: int | None | Unset = UNSET
    result: JobOutResultType0 | None | Unset = UNSET
    step: None | str | Unset = UNSET
    updated_at: None | str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.job_out_result_type_0 import JobOutResultType0

        id = self.id

        status = self.status

        type_ = self.type_

        created_at: None | str | Unset
        if isinstance(self.created_at, Unset):
            created_at = UNSET
        else:
            created_at = self.created_at

        error_message: None | str | Unset
        if isinstance(self.error_message, Unset):
            error_message = UNSET
        else:
            error_message = self.error_message

        progress: int | None | Unset
        if isinstance(self.progress, Unset):
            progress = UNSET
        else:
            progress = self.progress

        result: dict[str, Any] | None | Unset
        if isinstance(self.result, Unset):
            result = UNSET
        elif isinstance(self.result, JobOutResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        step: None | str | Unset
        if isinstance(self.step, Unset):
            step = UNSET
        else:
            step = self.step

        updated_at: None | str | Unset
        if isinstance(self.updated_at, Unset):
            updated_at = UNSET
        else:
            updated_at = self.updated_at

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "status": status,
                "type": type_,
            }
        )
        if created_at is not UNSET:
            field_dict["created_at"] = created_at
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if progress is not UNSET:
            field_dict["progress"] = progress
        if result is not UNSET:
            field_dict["result"] = result
        if step is not UNSET:
            field_dict["step"] = step
        if updated_at is not UNSET:
            field_dict["updated_at"] = updated_at

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_out_result_type_0 import JobOutResultType0

        d = dict(src_dict)
        id = d.pop("id")

        status = d.pop("status")

        type_ = d.pop("type")

        def _parse_created_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        created_at = _parse_created_at(d.pop("created_at", UNSET))

        def _parse_error_message(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        error_message = _parse_error_message(d.pop("error_message", UNSET))

        def _parse_progress(data: object) -> int | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(int | None | Unset, data)

        progress = _parse_progress(d.pop("progress", UNSET))

        def _parse_result(data: object) -> JobOutResultType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = JobOutResultType0.from_dict(data)

                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(JobOutResultType0 | None | Unset, data)

        result = _parse_result(d.pop("result", UNSET))

        def _parse_step(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        step = _parse_step(d.pop("step", UNSET))

        def _parse_updated_at(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        updated_at = _parse_updated_at(d.pop("updated_at", UNSET))

        job_out = cls(
            id=id,
            status=status,
            type_=type_,
            created_at=created_at,
            error_message=error_message,
            progress=progress,
            result=result,
            step=step,
            updated_at=updated_at,
        )

        job_out.additional_properties = d
        return job_out

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
