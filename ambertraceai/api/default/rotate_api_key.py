from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rotate_key_request import RotateKeyRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: RotateKeyRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/api-keys/{id}/rotate".format(
            id=quote(str(id), safe=""),
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
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RotateKeyRequest,
) -> Response[list[ValidationErrorModel]]:
    """Rotate API key

     Atomically issues a replacement for an existing API key and puts the old key into a bounded grace
    window (default 300s, max 24h; configurable via `grace_seconds`, 0 = immediate) after which it stops
    validating — rotate with zero downtime. The replacement inherits the old key's org, owner, platform
    binding, scope, name, rate limit, token budget, IP allowlist and expiry (override with
    `expires_at`). The new key secret is returned exactly once — store it securely. Send `{}` when using
    all defaults. Authorisation matches revoke: a session/user caller may rotate only THEIR OWN keys; an
    org-admin any org key; a user-scoped key only the platform keys it created. A revoked, expired, or
    already-rotated key cannot be rotated (409).

    Args:
        id (int): Resource ID
        body (RotateKeyRequest): Body for POST /api-keys/{id}/rotate. All fields optional.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RotateKeyRequest,
) -> list[ValidationErrorModel] | None:
    """Rotate API key

     Atomically issues a replacement for an existing API key and puts the old key into a bounded grace
    window (default 300s, max 24h; configurable via `grace_seconds`, 0 = immediate) after which it stops
    validating — rotate with zero downtime. The replacement inherits the old key's org, owner, platform
    binding, scope, name, rate limit, token budget, IP allowlist and expiry (override with
    `expires_at`). The new key secret is returned exactly once — store it securely. Send `{}` when using
    all defaults. Authorisation matches revoke: a session/user caller may rotate only THEIR OWN keys; an
    org-admin any org key; a user-scoped key only the platform keys it created. A revoked, expired, or
    already-rotated key cannot be rotated (409).

    Args:
        id (int): Resource ID
        body (RotateKeyRequest): Body for POST /api-keys/{id}/rotate. All fields optional.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RotateKeyRequest,
) -> Response[list[ValidationErrorModel]]:
    """Rotate API key

     Atomically issues a replacement for an existing API key and puts the old key into a bounded grace
    window (default 300s, max 24h; configurable via `grace_seconds`, 0 = immediate) after which it stops
    validating — rotate with zero downtime. The replacement inherits the old key's org, owner, platform
    binding, scope, name, rate limit, token budget, IP allowlist and expiry (override with
    `expires_at`). The new key secret is returned exactly once — store it securely. Send `{}` when using
    all defaults. Authorisation matches revoke: a session/user caller may rotate only THEIR OWN keys; an
    org-admin any org key; a user-scoped key only the platform keys it created. A revoked, expired, or
    already-rotated key cannot be rotated (409).

    Args:
        id (int): Resource ID
        body (RotateKeyRequest): Body for POST /api-keys/{id}/rotate. All fields optional.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RotateKeyRequest,
) -> list[ValidationErrorModel] | None:
    """Rotate API key

     Atomically issues a replacement for an existing API key and puts the old key into a bounded grace
    window (default 300s, max 24h; configurable via `grace_seconds`, 0 = immediate) after which it stops
    validating — rotate with zero downtime. The replacement inherits the old key's org, owner, platform
    binding, scope, name, rate limit, token budget, IP allowlist and expiry (override with
    `expires_at`). The new key secret is returned exactly once — store it securely. Send `{}` when using
    all defaults. Authorisation matches revoke: a session/user caller may rotate only THEIR OWN keys; an
    org-admin any org key; a user-scoped key only the platform keys it created. A revoked, expired, or
    already-rotated key cannot be rotated (409).

    Args:
        id (int): Resource ID
        body (RotateKeyRequest): Body for POST /api-keys/{id}/rotate. All fields optional.

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
            body=body,
        )
    ).parsed
