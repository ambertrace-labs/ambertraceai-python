from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rule_out import RuleOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    include_inactive: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["include_inactive"] = include_inactive

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/platforms/{id}/rules".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RuleOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = RuleOut.from_dict(response.json())

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
) -> Response[RuleOut | list[ValidationErrorModel]]:
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
    include_inactive: bool | Unset = False,
) -> Response[RuleOut | list[ValidationErrorModel]]:
    """List platform rules

     Returns the symbolic rules attached to a platform. By default only active rules (those that
    currently fire in queries) are returned; pass include_inactive=true to also include deactivated and
    pending rules. Each rule carries its id, name, description, rule_type, condition, action, priority,
    is_active flag, source, and scorecard.

    Args:
        id (int): Resource ID
        include_inactive (bool | Unset): When true, return inactive (deactivated/pending) rules as
            well as active ones. Defaults to active-only. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_inactive=include_inactive,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    include_inactive: bool | Unset = False,
) -> RuleOut | list[ValidationErrorModel] | None:
    """List platform rules

     Returns the symbolic rules attached to a platform. By default only active rules (those that
    currently fire in queries) are returned; pass include_inactive=true to also include deactivated and
    pending rules. Each rule carries its id, name, description, rule_type, condition, action, priority,
    is_active flag, source, and scorecard.

    Args:
        id (int): Resource ID
        include_inactive (bool | Unset): When true, return inactive (deactivated/pending) rules as
            well as active ones. Defaults to active-only. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
        include_inactive=include_inactive,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    include_inactive: bool | Unset = False,
) -> Response[RuleOut | list[ValidationErrorModel]]:
    """List platform rules

     Returns the symbolic rules attached to a platform. By default only active rules (those that
    currently fire in queries) are returned; pass include_inactive=true to also include deactivated and
    pending rules. Each rule carries its id, name, description, rule_type, condition, action, priority,
    is_active flag, source, and scorecard.

    Args:
        id (int): Resource ID
        include_inactive (bool | Unset): When true, return inactive (deactivated/pending) rules as
            well as active ones. Defaults to active-only. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        include_inactive=include_inactive,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    include_inactive: bool | Unset = False,
) -> RuleOut | list[ValidationErrorModel] | None:
    """List platform rules

     Returns the symbolic rules attached to a platform. By default only active rules (those that
    currently fire in queries) are returned; pass include_inactive=true to also include deactivated and
    pending rules. Each rule carries its id, name, description, rule_type, condition, action, priority,
    is_active flag, source, and scorecard.

    Args:
        id (int): Resource ID
        include_inactive (bool | Unset): When true, return inactive (deactivated/pending) rules as
            well as active ones. Defaults to active-only. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            include_inactive=include_inactive,
        )
    ).parsed
