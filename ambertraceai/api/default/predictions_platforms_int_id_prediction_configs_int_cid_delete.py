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
    cid: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/platforms/{id}/prediction-configs/{cid}".format(
            id=quote(str(id), safe=""),
            cid=quote(str(cid), safe=""),
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
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[ValidationErrorModel]]:
    """Delete prediction config

     Deletes a prediction config and all its trained models and forecast history. This cascades: the
    config, its trained model artifacts (on disk), and all stored forecasts are permanently removed.
    This action cannot be undone.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        cid=cid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> list[ValidationErrorModel] | None:
    """Delete prediction config

     Deletes a prediction config and all its trained models and forecast history. This cascades: the
    config, its trained model artifacts (on disk), and all stored forecasts are permanently removed.
    This action cannot be undone.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        cid=cid,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[ValidationErrorModel]]:
    """Delete prediction config

     Deletes a prediction config and all its trained models and forecast history. This cascades: the
    config, its trained model artifacts (on disk), and all stored forecasts are permanently removed.
    This action cannot be undone.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        cid=cid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> list[ValidationErrorModel] | None:
    """Delete prediction config

     Deletes a prediction config and all its trained models and forecast history. This cascades: the
    config, its trained model artifacts (on disk), and all stored forecasts are permanently removed.
    This action cannot be undone.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            cid=cid,
            client=client,
        )
    ).parsed
