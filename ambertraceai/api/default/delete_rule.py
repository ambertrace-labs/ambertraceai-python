from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rule_delete_out import RuleDeleteOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    rid: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "delete",
        "url": "/api/v1/platforms/{id}/rules/{rid}".format(
            id=quote(str(id), safe=""),
            rid=quote(str(rid), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RuleDeleteOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = RuleDeleteOut.from_dict(response.json())

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
) -> Response[RuleDeleteOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[RuleDeleteOut | list[ValidationErrorModel]]:
    """Delete rule

     Permanently deletes a rule from a platform. Returns 200 with {deleted: true}; 404 if the rule does
    not belong to the platform.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleDeleteOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        rid=rid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
) -> RuleDeleteOut | list[ValidationErrorModel] | None:
    """Delete rule

     Permanently deletes a rule from a platform. Returns 200 with {deleted: true}; 404 if the rule does
    not belong to the platform.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleDeleteOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        rid=rid,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[RuleDeleteOut | list[ValidationErrorModel]]:
    """Delete rule

     Permanently deletes a rule from a platform. Returns 200 with {deleted: true}; 404 if the rule does
    not belong to the platform.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleDeleteOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        rid=rid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
) -> RuleDeleteOut | list[ValidationErrorModel] | None:
    """Delete rule

     Permanently deletes a rule from a platform. Returns 200 with {deleted: true}; 404 if the rule does
    not belong to the platform.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleDeleteOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            rid=rid,
            client=client,
        )
    ).parsed
