from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.usage_stats_out import UsageStatsOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs() -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/usage",
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> UsageStatsOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = UsageStatsOut.from_dict(response.json())

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
) -> Response[UsageStatsOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[UsageStatsOut | list[ValidationErrorModel]]:
    """Get usage stats

     Returns API usage statistics: total requests, total tokens, average response time, and remaining
    token budget (if using an API key with a budget). For platform-scoped keys, returns stats for that
    platform only.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UsageStatsOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs()

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
) -> UsageStatsOut | list[ValidationErrorModel] | None:
    """Get usage stats

     Returns API usage statistics: total requests, total tokens, average response time, and remaining
    token budget (if using an API key with a budget). For platform-scoped keys, returns stats for that
    platform only.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UsageStatsOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
) -> Response[UsageStatsOut | list[ValidationErrorModel]]:
    """Get usage stats

     Returns API usage statistics: total requests, total tokens, average response time, and remaining
    token budget (if using an API key with a budget). For platform-scoped keys, returns stats for that
    platform only.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[UsageStatsOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs()

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
) -> UsageStatsOut | list[ValidationErrorModel] | None:
    """Get usage stats

     Returns API usage statistics: total requests, total tokens, average response time, and remaining
    token budget (if using an API key with a budget). For platform-scoped keys, returns stats for that
    platform only.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        UsageStatsOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
        )
    ).parsed
