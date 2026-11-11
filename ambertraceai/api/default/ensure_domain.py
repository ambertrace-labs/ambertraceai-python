from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.domain_ensure_out import DomainEnsureOut
from ...models.domain_ensure_request import DomainEnsureRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    *,
    body: DomainEnsureRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/domains/ensure",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DomainEnsureOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = DomainEnsureOut.from_dict(response.json())

        return response_200

    if response.status_code == 201:
        response_201 = DomainEnsureOut.from_dict(response.json())

        return response_201

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
) -> Response[DomainEnsureOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DomainEnsureRequest,
) -> Response[DomainEnsureOut | list[ValidationErrorModel]]:
    """Get or create domain

     Idempotent create: returns the caller's existing domain with exactly this name (earliest id), or
    creates it. 200 with created=false when reused, 201 with created=true when new. Concurrent callers
    converge on one row. Names are not unique per organisation, so only domains owned by the caller
    match.

    Args:
        body (DomainEnsureRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainEnsureOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: DomainEnsureRequest,
) -> DomainEnsureOut | list[ValidationErrorModel] | None:
    """Get or create domain

     Idempotent create: returns the caller's existing domain with exactly this name (earliest id), or
    creates it. 200 with created=false when reused, 201 with created=true when new. Concurrent callers
    converge on one row. Names are not unique per organisation, so only domains owned by the caller
    match.

    Args:
        body (DomainEnsureRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainEnsureOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: DomainEnsureRequest,
) -> Response[DomainEnsureOut | list[ValidationErrorModel]]:
    """Get or create domain

     Idempotent create: returns the caller's existing domain with exactly this name (earliest id), or
    creates it. 200 with created=false when reused, 201 with created=true when new. Concurrent callers
    converge on one row. Names are not unique per organisation, so only domains owned by the caller
    match.

    Args:
        body (DomainEnsureRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainEnsureOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: DomainEnsureRequest,
) -> DomainEnsureOut | list[ValidationErrorModel] | None:
    """Get or create domain

     Idempotent create: returns the caller's existing domain with exactly this name (earliest id), or
    creates it. 200 with created=false when reused, 201 with created=true when new. Concurrent callers
    converge on one row. Names are not unique per organisation, so only domains owned by the caller
    match.

    Args:
        body (DomainEnsureRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainEnsureOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
