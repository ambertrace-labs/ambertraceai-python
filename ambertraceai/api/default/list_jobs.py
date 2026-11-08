import datetime
from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.job_list_out import JobListOut
from ...models.list_jobs_ref_type_type_0 import ListJobsRefTypeType0
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    status: None | str | Unset = UNSET,
    ref_type: ListJobsRefTypeType0 | None | Unset = UNSET,
    ref_id: int | None | Unset = UNSET,
    type_: None | str | Unset = UNSET,
    since: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 20,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_ref_type: None | str | Unset
    if isinstance(ref_type, Unset):
        json_ref_type = UNSET
    elif isinstance(ref_type, ListJobsRefTypeType0):
        json_ref_type = ref_type.value
    else:
        json_ref_type = ref_type
    params["ref_type"] = json_ref_type

    json_ref_id: int | None | Unset
    if isinstance(ref_id, Unset):
        json_ref_id = UNSET
    else:
        json_ref_id = ref_id
    params["ref_id"] = json_ref_id

    json_type_: None | str | Unset
    if isinstance(type_, Unset):
        json_type_ = UNSET
    else:
        json_type_ = type_
    params["type"] = json_type_

    json_since: None | str | Unset
    if isinstance(since, Unset):
        json_since = UNSET
    elif isinstance(since, datetime.datetime):
        json_since = since.isoformat()
    else:
        json_since = since
    params["since"] = json_since

    params["limit"] = limit

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/jobs",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> JobListOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = JobListOut.from_dict(response.json())

        return response_200

    if response.status_code == 422:
        response_422 = []
        _response_422 = response.json()
        for response_422_item_data in _response_422:
            response_422_item = ValidationErrorModel.from_dict(response_422_item_data)

            response_422.append(response_422_item)

        return response_422

    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> Response[JobListOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    ref_type: ListJobsRefTypeType0 | None | Unset = UNSET,
    ref_id: int | None | Unset = UNSET,
    type_: None | str | Unset = UNSET,
    since: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 20,
) -> Response[JobListOut | list[ValidationErrorModel]]:
    r"""List jobs

     Discover the caller's in-flight and recent async jobs (cleaning, platform build, ontology build,
    prediction training / forecast, rule suggestion) across the organisation, newest first. Use it to
    re-attach to a long-running operation after navigating away or reloading: filter with
    status=pending,running and a ref_type/ref_id (platform|domain) or type, then poll GET /jobs/{id} for
    each id. Only jobs whose parent platform/domain the caller may view are returned. List items omit
    the job-type-specific `result` payload (fetch it with GET /jobs/{id}); a build or cleaning item has
    type \"build\"/\"cleaning\" — pass that as the `type` hint when polling, because job ids are unique
    only within a job type.

    Args:
        status (None | str | Unset): Comma-separated statuses: pending, running, completed,
            failed.
        ref_type (ListJobsRefTypeType0 | None | Unset): Restrict to jobs of a platform or a
            domain.
        ref_id (int | None | Unset): Restrict to jobs of this platform/domain id.
        type_ (None | str | Unset): Job type: "build", "cleaning", or a generic job type such as
            "ontology", "training", "symbolic_forecast".
        since (datetime.datetime | None | Unset): ISO-8601 cutoff: only jobs created at/after it
            (naive = UTC).
        limit (int | Unset): Max jobs returned (1-100). Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JobListOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        status=status,
        ref_type=ref_type,
        ref_id=ref_id,
        type_=type_,
        since=since,
        limit=limit,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    ref_type: ListJobsRefTypeType0 | None | Unset = UNSET,
    ref_id: int | None | Unset = UNSET,
    type_: None | str | Unset = UNSET,
    since: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 20,
) -> JobListOut | list[ValidationErrorModel] | None:
    r"""List jobs

     Discover the caller's in-flight and recent async jobs (cleaning, platform build, ontology build,
    prediction training / forecast, rule suggestion) across the organisation, newest first. Use it to
    re-attach to a long-running operation after navigating away or reloading: filter with
    status=pending,running and a ref_type/ref_id (platform|domain) or type, then poll GET /jobs/{id} for
    each id. Only jobs whose parent platform/domain the caller may view are returned. List items omit
    the job-type-specific `result` payload (fetch it with GET /jobs/{id}); a build or cleaning item has
    type \"build\"/\"cleaning\" — pass that as the `type` hint when polling, because job ids are unique
    only within a job type.

    Args:
        status (None | str | Unset): Comma-separated statuses: pending, running, completed,
            failed.
        ref_type (ListJobsRefTypeType0 | None | Unset): Restrict to jobs of a platform or a
            domain.
        ref_id (int | None | Unset): Restrict to jobs of this platform/domain id.
        type_ (None | str | Unset): Job type: "build", "cleaning", or a generic job type such as
            "ontology", "training", "symbolic_forecast".
        since (datetime.datetime | None | Unset): ISO-8601 cutoff: only jobs created at/after it
            (naive = UTC).
        limit (int | Unset): Max jobs returned (1-100). Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JobListOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        status=status,
        ref_type=ref_type,
        ref_id=ref_id,
        type_=type_,
        since=since,
        limit=limit,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    ref_type: ListJobsRefTypeType0 | None | Unset = UNSET,
    ref_id: int | None | Unset = UNSET,
    type_: None | str | Unset = UNSET,
    since: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 20,
) -> Response[JobListOut | list[ValidationErrorModel]]:
    r"""List jobs

     Discover the caller's in-flight and recent async jobs (cleaning, platform build, ontology build,
    prediction training / forecast, rule suggestion) across the organisation, newest first. Use it to
    re-attach to a long-running operation after navigating away or reloading: filter with
    status=pending,running and a ref_type/ref_id (platform|domain) or type, then poll GET /jobs/{id} for
    each id. Only jobs whose parent platform/domain the caller may view are returned. List items omit
    the job-type-specific `result` payload (fetch it with GET /jobs/{id}); a build or cleaning item has
    type \"build\"/\"cleaning\" — pass that as the `type` hint when polling, because job ids are unique
    only within a job type.

    Args:
        status (None | str | Unset): Comma-separated statuses: pending, running, completed,
            failed.
        ref_type (ListJobsRefTypeType0 | None | Unset): Restrict to jobs of a platform or a
            domain.
        ref_id (int | None | Unset): Restrict to jobs of this platform/domain id.
        type_ (None | str | Unset): Job type: "build", "cleaning", or a generic job type such as
            "ontology", "training", "symbolic_forecast".
        since (datetime.datetime | None | Unset): ISO-8601 cutoff: only jobs created at/after it
            (naive = UTC).
        limit (int | Unset): Max jobs returned (1-100). Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JobListOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        status=status,
        ref_type=ref_type,
        ref_id=ref_id,
        type_=type_,
        since=since,
        limit=limit,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    status: None | str | Unset = UNSET,
    ref_type: ListJobsRefTypeType0 | None | Unset = UNSET,
    ref_id: int | None | Unset = UNSET,
    type_: None | str | Unset = UNSET,
    since: datetime.datetime | None | Unset = UNSET,
    limit: int | Unset = 20,
) -> JobListOut | list[ValidationErrorModel] | None:
    r"""List jobs

     Discover the caller's in-flight and recent async jobs (cleaning, platform build, ontology build,
    prediction training / forecast, rule suggestion) across the organisation, newest first. Use it to
    re-attach to a long-running operation after navigating away or reloading: filter with
    status=pending,running and a ref_type/ref_id (platform|domain) or type, then poll GET /jobs/{id} for
    each id. Only jobs whose parent platform/domain the caller may view are returned. List items omit
    the job-type-specific `result` payload (fetch it with GET /jobs/{id}); a build or cleaning item has
    type \"build\"/\"cleaning\" — pass that as the `type` hint when polling, because job ids are unique
    only within a job type.

    Args:
        status (None | str | Unset): Comma-separated statuses: pending, running, completed,
            failed.
        ref_type (ListJobsRefTypeType0 | None | Unset): Restrict to jobs of a platform or a
            domain.
        ref_id (int | None | Unset): Restrict to jobs of this platform/domain id.
        type_ (None | str | Unset): Job type: "build", "cleaning", or a generic job type such as
            "ontology", "training", "symbolic_forecast".
        since (datetime.datetime | None | Unset): ISO-8601 cutoff: only jobs created at/after it
            (naive = UTC).
        limit (int | Unset): Max jobs returned (1-100). Default: 20.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JobListOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            status=status,
            ref_type=ref_type,
            ref_id=ref_id,
            type_=type_,
            since=since,
            limit=limit,
        )
    ).parsed
