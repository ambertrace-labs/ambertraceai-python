from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.credential_body import CredentialBody
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    provider: str,
    *,
    body: CredentialBody,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/connector-credentials/{provider}".format(
            provider=quote(str(provider), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    body: CredentialBody,
) -> Response[list[ValidationErrorModel]]:
    """Save a connector credential

     Stores (or replaces) the current user's API key for a connector provider (e.g. 'fred'), encrypted at
    rest. The key is then auto-injected when a connector config for that provider omits api_key. Returns
    masked metadata.

    Args:
        provider (str): Connector credential provider, e.g. 'fred'.
        body (CredentialBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        provider=provider,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    body: CredentialBody,
) -> list[ValidationErrorModel] | None:
    """Save a connector credential

     Stores (or replaces) the current user's API key for a connector provider (e.g. 'fred'), encrypted at
    rest. The key is then auto-injected when a connector config for that provider omits api_key. Returns
    masked metadata.

    Args:
        provider (str): Connector credential provider, e.g. 'fred'.
        body (CredentialBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        provider=provider,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    body: CredentialBody,
) -> Response[list[ValidationErrorModel]]:
    """Save a connector credential

     Stores (or replaces) the current user's API key for a connector provider (e.g. 'fred'), encrypted at
    rest. The key is then auto-injected when a connector config for that provider omits api_key. Returns
    masked metadata.

    Args:
        provider (str): Connector credential provider, e.g. 'fred'.
        body (CredentialBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        provider=provider,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    provider: str,
    *,
    client: AuthenticatedClient | Client,
    body: CredentialBody,
) -> list[ValidationErrorModel] | None:
    """Save a connector credential

     Stores (or replaces) the current user's API key for a connector provider (e.g. 'fred'), encrypted at
    rest. The key is then auto-injected when a connector config for that provider omits api_key. Returns
    masked metadata.

    Args:
        provider (str): Connector credential provider, e.g. 'fred'.
        body (CredentialBody):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            provider=provider,
            client=client,
            body=body,
        )
    ).parsed
