from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.job_out import JobOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/jobs/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> JobOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = JobOut.from_dict(response.json())

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
) -> Response[JobOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[JobOut | list[ValidationErrorModel]]:
    """Get job status

     Polls the status of an async job (cleaning, platform build, ontology build, prediction training, or
    rule suggestion). Returns the job type, status (pending/running/completed/failed), progress
    percentage, current step, error message if failed, and a job-type-specific result payload when
    completed (rule-suggestion jobs carry stats, rejected_rules, and the stored suggestions; platform-
    build jobs carry build_quality — a customer-safe status (ok/warnings/needs_review) with severity-
    graded checks summarising whether the build produced a usable decision layer — alongside the
    underlying generation_diagnostics detail). Use this to track async operations started by POST
    /datasets/{id}/clean, POST /platforms, POST /domains/{id}/build-ontology, POST
    /platforms/{id}/prediction-configs/{cid}/train, or POST /platforms/{id}/suggest-rules.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JobOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> JobOut | list[ValidationErrorModel] | None:
    """Get job status

     Polls the status of an async job (cleaning, platform build, ontology build, prediction training, or
    rule suggestion). Returns the job type, status (pending/running/completed/failed), progress
    percentage, current step, error message if failed, and a job-type-specific result payload when
    completed (rule-suggestion jobs carry stats, rejected_rules, and the stored suggestions; platform-
    build jobs carry build_quality — a customer-safe status (ok/warnings/needs_review) with severity-
    graded checks summarising whether the build produced a usable decision layer — alongside the
    underlying generation_diagnostics detail). Use this to track async operations started by POST
    /datasets/{id}/clean, POST /platforms, POST /domains/{id}/build-ontology, POST
    /platforms/{id}/prediction-configs/{cid}/train, or POST /platforms/{id}/suggest-rules.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JobOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[JobOut | list[ValidationErrorModel]]:
    """Get job status

     Polls the status of an async job (cleaning, platform build, ontology build, prediction training, or
    rule suggestion). Returns the job type, status (pending/running/completed/failed), progress
    percentage, current step, error message if failed, and a job-type-specific result payload when
    completed (rule-suggestion jobs carry stats, rejected_rules, and the stored suggestions; platform-
    build jobs carry build_quality — a customer-safe status (ok/warnings/needs_review) with severity-
    graded checks summarising whether the build produced a usable decision layer — alongside the
    underlying generation_diagnostics detail). Use this to track async operations started by POST
    /datasets/{id}/clean, POST /platforms, POST /domains/{id}/build-ontology, POST
    /platforms/{id}/prediction-configs/{cid}/train, or POST /platforms/{id}/suggest-rules.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[JobOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> JobOut | list[ValidationErrorModel] | None:
    """Get job status

     Polls the status of an async job (cleaning, platform build, ontology build, prediction training, or
    rule suggestion). Returns the job type, status (pending/running/completed/failed), progress
    percentage, current step, error message if failed, and a job-type-specific result payload when
    completed (rule-suggestion jobs carry stats, rejected_rules, and the stored suggestions; platform-
    build jobs carry build_quality — a customer-safe status (ok/warnings/needs_review) with severity-
    graded checks summarising whether the build produced a usable decision layer — alongside the
    underlying generation_diagnostics detail). Use this to track async operations started by POST
    /datasets/{id}/clean, POST /platforms, POST /domains/{id}/build-ontology, POST
    /platforms/{id}/prediction-configs/{cid}/train, or POST /platforms/{id}/suggest-rules.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        JobOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
