from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/platforms/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> list[ValidationErrorModel] | None:
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
) -> Response[list[ValidationErrorModel]]:
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
) -> Response[list[ValidationErrorModel]]:
    """Delete platform

     Permanently deletes a platform and everything derived from it: build jobs, symbolic rules and rule
    feedback, reports, query audit logs, standing findings, prediction configs/models/forecasts,
    suggestor usage, usage logs, and any platform-scoped API keys. This is a lifecycle operation:
    session users and user-scoped (agent) keys may delete platforms in their own organisation; platform-
    scoped keys are query-only and cannot delete. Irreversible.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
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
) -> list[ValidationErrorModel] | None:
    """Delete platform

     Permanently deletes a platform and everything derived from it: build jobs, symbolic rules and rule
    feedback, reports, query audit logs, standing findings, prediction configs/models/forecasts,
    suggestor usage, usage logs, and any platform-scoped API keys. This is a lifecycle operation:
    session users and user-scoped (agent) keys may delete platforms in their own organisation; platform-
    scoped keys are query-only and cannot delete. Irreversible.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[ValidationErrorModel]]:
    """Delete platform

     Permanently deletes a platform and everything derived from it: build jobs, symbolic rules and rule
    feedback, reports, query audit logs, standing findings, prediction configs/models/forecasts,
    suggestor usage, usage logs, and any platform-scoped API keys. This is a lifecycle operation:
    session users and user-scoped (agent) keys may delete platforms in their own organisation; platform-
    scoped keys are query-only and cannot delete. Irreversible.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
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
) -> list[ValidationErrorModel] | None:
    """Delete platform

     Permanently deletes a platform and everything derived from it: build jobs, symbolic rules and rule
    feedback, reports, query audit logs, standing findings, prediction configs/models/forecasts,
    suggestor usage, usage logs, and any platform-scoped API keys. This is a lifecycle operation:
    session users and user-scoped (agent) keys may delete platforms in their own organisation; platform-
    scoped keys are query-only and cannot delete. Irreversible.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
