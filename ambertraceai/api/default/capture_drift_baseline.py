from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.drift_baseline_out import DriftBaselineOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/drift/baseline".format(
            id=quote(str(id), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DriftBaselineOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = DriftBaselineOut.from_dict(response.json())

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
) -> Response[DriftBaselineOut | list[ValidationErrorModel]]:
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
) -> Response[DriftBaselineOut | list[ValidationErrorModel]]:
    """Capture drift baseline

     Captures the current drift metrics (certified-fact rejection rate and per-rule firing rates over
    recent query history) as the approval-time baseline for this platform, stored in the platform
    config. Call this at approval time so later drift checks have a reference point. Lifecycle
    operation: session users and user-scoped keys only.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DriftBaselineOut | list[ValidationErrorModel]]
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
) -> DriftBaselineOut | list[ValidationErrorModel] | None:
    """Capture drift baseline

     Captures the current drift metrics (certified-fact rejection rate and per-rule firing rates over
    recent query history) as the approval-time baseline for this platform, stored in the platform
    config. Call this at approval time so later drift checks have a reference point. Lifecycle
    operation: session users and user-scoped keys only.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DriftBaselineOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[DriftBaselineOut | list[ValidationErrorModel]]:
    """Capture drift baseline

     Captures the current drift metrics (certified-fact rejection rate and per-rule firing rates over
    recent query history) as the approval-time baseline for this platform, stored in the platform
    config. Call this at approval time so later drift checks have a reference point. Lifecycle
    operation: session users and user-scoped keys only.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DriftBaselineOut | list[ValidationErrorModel]]
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
) -> DriftBaselineOut | list[ValidationErrorModel] | None:
    """Capture drift baseline

     Captures the current drift metrics (certified-fact rejection rate and per-rule firing rates over
    recent query history) as the approval-time baseline for this platform, stored in the platform
    config. Call this at approval time so later drift checks have a reference point. Lifecycle
    operation: session users and user-scoped keys only.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DriftBaselineOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
