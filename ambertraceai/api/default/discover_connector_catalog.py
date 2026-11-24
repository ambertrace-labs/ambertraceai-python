from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    connector_type: str,
    *,
    route: None | str | Unset = UNSET,
    search_text: None | str | Unset = UNSET,
    category_id: int | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    report: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_route: None | str | Unset
    if isinstance(route, Unset):
        json_route = UNSET
    else:
        json_route = route
    params["route"] = json_route

    json_search_text: None | str | Unset
    if isinstance(search_text, Unset):
        json_search_text = UNSET
    else:
        json_search_text = search_text
    params["search_text"] = json_search_text

    json_category_id: int | None | Unset
    if isinstance(category_id, Unset):
        json_category_id = UNSET
    else:
        json_category_id = category_id
    params["category_id"] = json_category_id

    json_q: None | str | Unset
    if isinstance(q, Unset):
        json_q = UNSET
    else:
        json_q = q
    params["q"] = json_q

    json_report: None | str | Unset
    if isinstance(report, Unset):
        json_report = UNSET
    else:
        json_report = report
    params["report"] = json_report

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/connectors/{connector_type}/discover".format(
            connector_type=quote(str(connector_type), safe=""),
        ),
        "params": params,
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
    connector_type: str,
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
    search_text: None | str | Unset = UNSET,
    category_id: int | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    report: None | str | Unset = UNSET,
) -> Response[list[ValidationErrorModel]]:
    r"""Browse a connector series catalog

     Browses the series catalog of a connector that supports discovery (eia, fred, fred_sentiment, yahoo,
    cftc). Parameters are connector-specific query params: eia \"route\"; fred \"search_text\" (series
    search) or \"category_id\" (category browse, default root); yahoo \"q\" (symbol search, required;
    unofficial upstream endpoint); cftc \"report\" (disaggregated/legacy/financial). Returns 422 for a
    connector that does not support discovery or a missing/invalid parameter or API key.

    Args:
        connector_type (str): Connector type to browse (e.g. 'fred', 'yahoo', 'cftc', 'eia').
        route (None | str | Unset): eia: EIA v2 route to browse (omit for top-level routes).
        search_text (None | str | Unset): fred: series search text.
        category_id (int | None | Unset): fred: category ID to browse (default 0 = root).
        q (None | str | Unset): yahoo: symbol search text (required for yahoo).
        report (None | str | Unset): cftc: report type (disaggregated, legacy, financial).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        connector_type=connector_type,
        route=route,
        search_text=search_text,
        category_id=category_id,
        q=q,
        report=report,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    connector_type: str,
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
    search_text: None | str | Unset = UNSET,
    category_id: int | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    report: None | str | Unset = UNSET,
) -> list[ValidationErrorModel] | None:
    r"""Browse a connector series catalog

     Browses the series catalog of a connector that supports discovery (eia, fred, fred_sentiment, yahoo,
    cftc). Parameters are connector-specific query params: eia \"route\"; fred \"search_text\" (series
    search) or \"category_id\" (category browse, default root); yahoo \"q\" (symbol search, required;
    unofficial upstream endpoint); cftc \"report\" (disaggregated/legacy/financial). Returns 422 for a
    connector that does not support discovery or a missing/invalid parameter or API key.

    Args:
        connector_type (str): Connector type to browse (e.g. 'fred', 'yahoo', 'cftc', 'eia').
        route (None | str | Unset): eia: EIA v2 route to browse (omit for top-level routes).
        search_text (None | str | Unset): fred: series search text.
        category_id (int | None | Unset): fred: category ID to browse (default 0 = root).
        q (None | str | Unset): yahoo: symbol search text (required for yahoo).
        report (None | str | Unset): cftc: report type (disaggregated, legacy, financial).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        connector_type=connector_type,
        client=client,
        route=route,
        search_text=search_text,
        category_id=category_id,
        q=q,
        report=report,
    ).parsed


async def asyncio_detailed(
    connector_type: str,
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
    search_text: None | str | Unset = UNSET,
    category_id: int | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    report: None | str | Unset = UNSET,
) -> Response[list[ValidationErrorModel]]:
    r"""Browse a connector series catalog

     Browses the series catalog of a connector that supports discovery (eia, fred, fred_sentiment, yahoo,
    cftc). Parameters are connector-specific query params: eia \"route\"; fred \"search_text\" (series
    search) or \"category_id\" (category browse, default root); yahoo \"q\" (symbol search, required;
    unofficial upstream endpoint); cftc \"report\" (disaggregated/legacy/financial). Returns 422 for a
    connector that does not support discovery or a missing/invalid parameter or API key.

    Args:
        connector_type (str): Connector type to browse (e.g. 'fred', 'yahoo', 'cftc', 'eia').
        route (None | str | Unset): eia: EIA v2 route to browse (omit for top-level routes).
        search_text (None | str | Unset): fred: series search text.
        category_id (int | None | Unset): fred: category ID to browse (default 0 = root).
        q (None | str | Unset): yahoo: symbol search text (required for yahoo).
        report (None | str | Unset): cftc: report type (disaggregated, legacy, financial).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        connector_type=connector_type,
        route=route,
        search_text=search_text,
        category_id=category_id,
        q=q,
        report=report,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    connector_type: str,
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
    search_text: None | str | Unset = UNSET,
    category_id: int | None | Unset = UNSET,
    q: None | str | Unset = UNSET,
    report: None | str | Unset = UNSET,
) -> list[ValidationErrorModel] | None:
    r"""Browse a connector series catalog

     Browses the series catalog of a connector that supports discovery (eia, fred, fred_sentiment, yahoo,
    cftc). Parameters are connector-specific query params: eia \"route\"; fred \"search_text\" (series
    search) or \"category_id\" (category browse, default root); yahoo \"q\" (symbol search, required;
    unofficial upstream endpoint); cftc \"report\" (disaggregated/legacy/financial). Returns 422 for a
    connector that does not support discovery or a missing/invalid parameter or API key.

    Args:
        connector_type (str): Connector type to browse (e.g. 'fred', 'yahoo', 'cftc', 'eia').
        route (None | str | Unset): eia: EIA v2 route to browse (omit for top-level routes).
        search_text (None | str | Unset): fred: series search text.
        category_id (int | None | Unset): fred: category ID to browse (default 0 = root).
        q (None | str | Unset): yahoo: symbol search text (required for yahoo).
        report (None | str | Unset): cftc: report type (disaggregated, legacy, financial).

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            connector_type=connector_type,
            client=client,
            route=route,
            search_text=search_text,
            category_id=category_id,
            q=q,
            report=report,
        )
    ).parsed
