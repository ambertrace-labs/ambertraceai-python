from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.platform_out import PlatformOut
from ...models.platform_update_request import PlatformUpdateRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: PlatformUpdateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "patch",
        "url": "/api/v1/platforms/{id}".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PlatformOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = PlatformOut.from_dict(response.json())

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
) -> Response[PlatformOut | list[ValidationErrorModel]]:
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
    body: PlatformUpdateRequest,
) -> Response[PlatformOut | list[ValidationErrorModel]]:
    """Update platform verified-profile settings

     Updates a platform's verified-profile settings: enable/disable the verified profile, set the
    certified-fact confidence threshold (τ, verified_min_confidence), and set the required-invariant
    manifest. Only the fields provided are applied. Enabling the verified profile re-validates the
    platform's existing active rules: if any are not verified-profile-safe the flip is rejected with a
    list of the offending rules. Setting an invariant_manifest on a verified platform (or flipping
    verified on with a stored manifest) runs the same invariant gate as a build: if any forbid/require
    obligation is not satisfied by the active rules, the update is rejected (409) with the violations —
    it is never stored unvalidated. Lifecycle operation: session users and user-scoped keys only;
    platform-scoped keys are query-only.

    Args:
        id (int): Resource ID
        body (PlatformUpdateRequest): Mutable verified-profile settings for an existing platform
            (C1a/C1c).

            All fields optional — only those provided are applied. Flipping
            ``verified_profile`` to ``True`` triggers a safe-flip validation of the
            platform's existing active rules (see ``BuilderService.update_platform``).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PlatformOut | list[ValidationErrorModel]]
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
    body: PlatformUpdateRequest,
) -> PlatformOut | list[ValidationErrorModel] | None:
    """Update platform verified-profile settings

     Updates a platform's verified-profile settings: enable/disable the verified profile, set the
    certified-fact confidence threshold (τ, verified_min_confidence), and set the required-invariant
    manifest. Only the fields provided are applied. Enabling the verified profile re-validates the
    platform's existing active rules: if any are not verified-profile-safe the flip is rejected with a
    list of the offending rules. Setting an invariant_manifest on a verified platform (or flipping
    verified on with a stored manifest) runs the same invariant gate as a build: if any forbid/require
    obligation is not satisfied by the active rules, the update is rejected (409) with the violations —
    it is never stored unvalidated. Lifecycle operation: session users and user-scoped keys only;
    platform-scoped keys are query-only.

    Args:
        id (int): Resource ID
        body (PlatformUpdateRequest): Mutable verified-profile settings for an existing platform
            (C1a/C1c).

            All fields optional — only those provided are applied. Flipping
            ``verified_profile`` to ``True`` triggers a safe-flip validation of the
            platform's existing active rules (see ``BuilderService.update_platform``).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PlatformOut | list[ValidationErrorModel]
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
    body: PlatformUpdateRequest,
) -> Response[PlatformOut | list[ValidationErrorModel]]:
    """Update platform verified-profile settings

     Updates a platform's verified-profile settings: enable/disable the verified profile, set the
    certified-fact confidence threshold (τ, verified_min_confidence), and set the required-invariant
    manifest. Only the fields provided are applied. Enabling the verified profile re-validates the
    platform's existing active rules: if any are not verified-profile-safe the flip is rejected with a
    list of the offending rules. Setting an invariant_manifest on a verified platform (or flipping
    verified on with a stored manifest) runs the same invariant gate as a build: if any forbid/require
    obligation is not satisfied by the active rules, the update is rejected (409) with the violations —
    it is never stored unvalidated. Lifecycle operation: session users and user-scoped keys only;
    platform-scoped keys are query-only.

    Args:
        id (int): Resource ID
        body (PlatformUpdateRequest): Mutable verified-profile settings for an existing platform
            (C1a/C1c).

            All fields optional — only those provided are applied. Flipping
            ``verified_profile`` to ``True`` triggers a safe-flip validation of the
            platform's existing active rules (see ``BuilderService.update_platform``).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PlatformOut | list[ValidationErrorModel]]
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
    body: PlatformUpdateRequest,
) -> PlatformOut | list[ValidationErrorModel] | None:
    """Update platform verified-profile settings

     Updates a platform's verified-profile settings: enable/disable the verified profile, set the
    certified-fact confidence threshold (τ, verified_min_confidence), and set the required-invariant
    manifest. Only the fields provided are applied. Enabling the verified profile re-validates the
    platform's existing active rules: if any are not verified-profile-safe the flip is rejected with a
    list of the offending rules. Setting an invariant_manifest on a verified platform (or flipping
    verified on with a stored manifest) runs the same invariant gate as a build: if any forbid/require
    obligation is not satisfied by the active rules, the update is rejected (409) with the violations —
    it is never stored unvalidated. Lifecycle operation: session users and user-scoped keys only;
    platform-scoped keys are query-only.

    Args:
        id (int): Resource ID
        body (PlatformUpdateRequest): Mutable verified-profile settings for an existing platform
            (C1a/C1c).

            All fields optional — only those provided are applied. Flipping
            ``verified_profile`` to ``True`` triggers a safe-flip validation of the
            platform's existing active rules (see ``BuilderService.update_platform``).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PlatformOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
