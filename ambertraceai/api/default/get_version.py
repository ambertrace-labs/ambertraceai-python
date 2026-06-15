from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...models.version_response import VersionResponse
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/version",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VersionResponse | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = VersionResponse.from_dict(response.json())

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
) -> Response[VersionResponse | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[VersionResponse | list[ValidationErrorModel]]:
    """App version

     Returns the running app version, git commit SHA, and build time. No authentication required. Use
    this to confirm exactly which deploy you are hitting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VersionResponse | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> VersionResponse | list[ValidationErrorModel] | None:
    """App version

     Returns the running app version, git commit SHA, and build time. No authentication required. Use
    this to confirm exactly which deploy you are hitting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VersionResponse | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[VersionResponse | list[ValidationErrorModel]]:
    """App version

     Returns the running app version, git commit SHA, and build time. No authentication required. Use
    this to confirm exactly which deploy you are hitting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VersionResponse | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> VersionResponse | list[ValidationErrorModel] | None:
    """App version

     Returns the running app version, git commit SHA, and build time. No authentication required. Use
    this to confirm exactly which deploy you are hitting.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VersionResponse | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
