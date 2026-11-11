from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.domain_search_out import DomainSearchOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    min_entity_count: int | Unset = 0,
    with_entity_count: bool | Unset = False,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

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

    params["limit"] = limit

    params["offset"] = offset

    params["min_entity_count"] = min_entity_count

    params["with_entity_count"] = with_entity_count

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/domains/search",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DomainSearchOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = DomainSearchOut.from_dict(response.json())

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
) -> Response[DomainSearchOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    min_entity_count: int | Unset = 0,
    with_entity_count: bool | Unset = False,
) -> Response[DomainSearchOut | list[ValidationErrorModel]]:
    """Search domains (typeahead)

     Lightweight domain lookup for pickers: returns only {id, name, status}, ordered by name, one SQL
    page at a time (never the whole collection). Optional q (case-insensitive substring of name or
    description) and status (comma-separated); limit (default 20, max 100) / offset.
    with_entity_count=true adds entity_count per row; min_entity_count=N keeps only domains with at
    least N ontology entities (e.g. 1 = can build a platform). pagination.total is the true match count.

    Args:
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'active').
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.
        min_entity_count (int | Unset): Only domains with at least this many ontology entities
            (applied server-side). Default: 0.
        with_entity_count (bool | Unset): Also return entity_count (ontology entities) per row, so
            a picker can exclude domains that cannot build a platform yet. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainSearchOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        limit=limit,
        offset=offset,
        min_entity_count=min_entity_count,
        with_entity_count=with_entity_count,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    min_entity_count: int | Unset = 0,
    with_entity_count: bool | Unset = False,
) -> DomainSearchOut | list[ValidationErrorModel] | None:
    """Search domains (typeahead)

     Lightweight domain lookup for pickers: returns only {id, name, status}, ordered by name, one SQL
    page at a time (never the whole collection). Optional q (case-insensitive substring of name or
    description) and status (comma-separated); limit (default 20, max 100) / offset.
    with_entity_count=true adds entity_count per row; min_entity_count=N keeps only domains with at
    least N ontology entities (e.g. 1 = can build a platform). pagination.total is the true match count.

    Args:
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'active').
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.
        min_entity_count (int | Unset): Only domains with at least this many ontology entities
            (applied server-side). Default: 0.
        with_entity_count (bool | Unset): Also return entity_count (ontology entities) per row, so
            a picker can exclude domains that cannot build a platform yet. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainSearchOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        q=q,
        status=status,
        limit=limit,
        offset=offset,
        min_entity_count=min_entity_count,
        with_entity_count=with_entity_count,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    min_entity_count: int | Unset = 0,
    with_entity_count: bool | Unset = False,
) -> Response[DomainSearchOut | list[ValidationErrorModel]]:
    """Search domains (typeahead)

     Lightweight domain lookup for pickers: returns only {id, name, status}, ordered by name, one SQL
    page at a time (never the whole collection). Optional q (case-insensitive substring of name or
    description) and status (comma-separated); limit (default 20, max 100) / offset.
    with_entity_count=true adds entity_count per row; min_entity_count=N keeps only domains with at
    least N ontology entities (e.g. 1 = can build a platform). pagination.total is the true match count.

    Args:
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'active').
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.
        min_entity_count (int | Unset): Only domains with at least this many ontology entities
            (applied server-side). Default: 0.
        with_entity_count (bool | Unset): Also return entity_count (ontology entities) per row, so
            a picker can exclude domains that cannot build a platform yet. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DomainSearchOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        q=q,
        status=status,
        limit=limit,
        offset=offset,
        min_entity_count=min_entity_count,
        with_entity_count=with_entity_count,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    q: None | str | Unset = UNSET,
    status: None | str | Unset = UNSET,
    limit: int | Unset = 20,
    offset: int | Unset = 0,
    min_entity_count: int | Unset = 0,
    with_entity_count: bool | Unset = False,
) -> DomainSearchOut | list[ValidationErrorModel] | None:
    """Search domains (typeahead)

     Lightweight domain lookup for pickers: returns only {id, name, status}, ordered by name, one SQL
    page at a time (never the whole collection). Optional q (case-insensitive substring of name or
    description) and status (comma-separated); limit (default 20, max 100) / offset.
    with_entity_count=true adds entity_count per row; min_entity_count=N keeps only domains with at
    least N ontology entities (e.g. 1 = can build a platform). pagination.total is the true match count.

    Args:
        q (None | str | Unset): Case-insensitive substring match on domain name or description.
        status (None | str | Unset): Comma-separated statuses (e.g. 'active').
        limit (int | Unset):  Default: 20.
        offset (int | Unset):  Default: 0.
        min_entity_count (int | Unset): Only domains with at least this many ontology entities
            (applied server-side). Default: 0.
        with_entity_count (bool | Unset): Also return entity_count (ontology entities) per row, so
            a picker can exclude domains that cannot build a platform yet. Default: False.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DomainSearchOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            q=q,
            status=status,
            limit=limit,
            offset=offset,
            min_entity_count=min_entity_count,
            with_entity_count=with_entity_count,
        )
    ).parsed
