from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="VerifyPropertyStarted")


@_attrs_define
class VerifyPropertyStarted:
    """202 envelope of the async ``verify_property`` start: poll ``GET /jobs/{job_id}``.
    The completed job ``result`` is a :class:`VerifyPropertyResponse`.

        Attributes:
            job_id (int): Poll GET /api/v1/jobs/{job_id} until completed.
            platform_id (int):
            poll (str): The poll path, /api/v1/jobs/{job_id}.
            status (str): 'verifying' while the job runs.
    """

    job_id: int
    platform_id: int
    poll: str
    status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_id = self.job_id

        platform_id = self.platform_id

        poll = self.poll

        status = self.status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "job_id": job_id,
                "platform_id": platform_id,
                "poll": poll,
                "status": status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        job_id = d.pop("job_id")

        platform_id = d.pop("platform_id")

        poll = d.pop("poll")

        status = d.pop("status")

        verify_property_started = cls(
            job_id=job_id,
            platform_id=platform_id,
            poll=poll,
            status=status,
        )

        verify_property_started.additional_properties = d
        return verify_property_started

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
