from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.domain_out import DomainOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    sort: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["limit"] = limit

    params["offset"] = offset

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    json_status: None | str | Unset
    if isinstance(status, Unset):
        json_status = UNSET
    else:
        json_status = status
    params["status"] = json_status

    json_sort: None | str | Unset
    if isinstance(sort, Unset):
        json_sort = UNSET
    else:
        json_sort = sort
    params["sort"] = json_sort

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/domains",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DomainOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = DomainOut.from_dict(response.json())

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
) -> Response[DomainOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    sort: None | str | Unset = UNSET,
) -> Response[DomainOut | list[ValidationErrorModel]]:
    """List domains

     Returns the domains visible to the caller in the authenticated organisation. Server-side pagination
    (limit/offset; pagination.total is the true count). Optional filters: q (case-insensitive substring
    of name or description), status (comma-separated), sort (id | name | status | updated | created;
    prefix '-' for descending; default id). For a lightweight typeahead use GET /domains/search.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'draft,active').
        sort (None | str | Unset): id | name | status | updated | created; prefix '-' for
            descending. Default: id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        q=q,
        status=status,
        sort=sort,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    sort: None | str | Unset = UNSET,
) -> DomainOut | list[ValidationErrorModel] | None:
    """List domains

     Returns the domains visible to the caller in the authenticated organisation. Server-side pagination
    (limit/offset; pagination.total is the true count). Optional filters: q (case-insensitive substring
    of name or description), status (comma-separated), sort (id | name | status | updated | created;
    prefix '-' for descending; default id). For a lightweight typeahead use GET /domains/search.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'draft,active').
        sort (None | str | Unset): id | name | status | updated | created; prefix '-' for
            descending. Default: id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        limit=limit,
        offset=offset,
        q=q,
        status=status,
        sort=sort,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    sort: None | str | Unset = UNSET,
) -> Response[DomainOut | list[ValidationErrorModel]]:
    """List domains

     Returns the domains visible to the caller in the authenticated organisation. Server-side pagination
    (limit/offset; pagination.total is the true count). Optional filters: q (case-insensitive substring
    of name or description), status (comma-separated), sort (id | name | status | updated | created;
    prefix '-' for descending; default id). For a lightweight typeahead use GET /domains/search.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'draft,active').
        sort (None | str | Unset): id | name | status | updated | created; prefix '-' for
            descending. Default: id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        limit=limit,
        offset=offset,
        q=q,
        status=status,
        sort=sort,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    limit: int | Unset = 50,
    offset: int | Unset = 0,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    sort: None | str | Unset = UNSET,
) -> DomainOut | list[ValidationErrorModel] | None:
    """List domains

     Returns the domains visible to the caller in the authenticated organisation. Server-side pagination
    (limit/offset; pagination.total is the true count). Optional filters: q (case-insensitive substring
    of name or description), status (comma-separated), sort (id | name | status | updated | created;
    prefix '-' for descending; default id). For a lightweight typeahead use GET /domains/search.

    Args:
        limit (int | Unset):  Default: 50.
        offset (int | Unset):  Default: 0.
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'draft,active').
        sort (None | str | Unset): id | name | status | updated | created; prefix '-' for
            descending. Default: id.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            limit=limit,
            offset=offset,
            q=q,
            status=status,
            sort=sort,
        )
    ).parsed
