from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    route: None | str | Unset = UNSET,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    json_route: None | str | Unset
    if isinstance(route, Unset):
        json_route = UNSET
    else:
        json_route = route
    params["route"] = json_route

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/connectors/eia/discover",
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
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
) -> Response[list[ValidationErrorModel]]:
    r"""Browse the EIA v2 general data catalog

     Browses the EIA v2 API catalog: omit \"route\" for the 14 top-level routes (electricity, petroleum,
    natural-gas, coal, nuclear, renewables, CO2 emissions, international, ...), pass a top-level route
    (e.g. \"electricity\") for its child routes, or a full leaf dataset route (e.g.
    \"electricity/retail-sales\") for its queryable facets, data columns, and supported frequencies.
    Feed the returned facet IDs into the eia connector Mode B \"facets\" config for a general (non-oil-
    preset) EIA pull. Returns the raw v2 metadata unmodified.

    Args:
        route (None | str | Unset): An EIA v2 API route to browse. Omit for the 14 top-level
            routes (e.g. 'electricity', 'petroleum'), pass a top-level route for its child routes, or
            a full leaf dataset route (e.g. 'electricity/retail-sales') for its queryable facets, data
            columns, and supported frequencies -- feed the facet IDs into the eia connector's Mode B
            'facets' config.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        route=route,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
) -> list[ValidationErrorModel] | None:
    r"""Browse the EIA v2 general data catalog

     Browses the EIA v2 API catalog: omit \"route\" for the 14 top-level routes (electricity, petroleum,
    natural-gas, coal, nuclear, renewables, CO2 emissions, international, ...), pass a top-level route
    (e.g. \"electricity\") for its child routes, or a full leaf dataset route (e.g.
    \"electricity/retail-sales\") for its queryable facets, data columns, and supported frequencies.
    Feed the returned facet IDs into the eia connector Mode B \"facets\" config for a general (non-oil-
    preset) EIA pull. Returns the raw v2 metadata unmodified.

    Args:
        route (None | str | Unset): An EIA v2 API route to browse. Omit for the 14 top-level
            routes (e.g. 'electricity', 'petroleum'), pass a top-level route for its child routes, or
            a full leaf dataset route (e.g. 'electricity/retail-sales') for its queryable facets, data
            columns, and supported frequencies -- feed the facet IDs into the eia connector's Mode B
            'facets' config.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        route=route,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
) -> Response[list[ValidationErrorModel]]:
    r"""Browse the EIA v2 general data catalog

     Browses the EIA v2 API catalog: omit \"route\" for the 14 top-level routes (electricity, petroleum,
    natural-gas, coal, nuclear, renewables, CO2 emissions, international, ...), pass a top-level route
    (e.g. \"electricity\") for its child routes, or a full leaf dataset route (e.g.
    \"electricity/retail-sales\") for its queryable facets, data columns, and supported frequencies.
    Feed the returned facet IDs into the eia connector Mode B \"facets\" config for a general (non-oil-
    preset) EIA pull. Returns the raw v2 metadata unmodified.

    Args:
        route (None | str | Unset): An EIA v2 API route to browse. Omit for the 14 top-level
            routes (e.g. 'electricity', 'petroleum'), pass a top-level route for its child routes, or
            a full leaf dataset route (e.g. 'electricity/retail-sales') for its queryable facets, data
            columns, and supported frequencies -- feed the facet IDs into the eia connector's Mode B
            'facets' config.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        route=route,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    route: None | str | Unset = UNSET,
) -> list[ValidationErrorModel] | None:
    r"""Browse the EIA v2 general data catalog

     Browses the EIA v2 API catalog: omit \"route\" for the 14 top-level routes (electricity, petroleum,
    natural-gas, coal, nuclear, renewables, CO2 emissions, international, ...), pass a top-level route
    (e.g. \"electricity\") for its child routes, or a full leaf dataset route (e.g.
    \"electricity/retail-sales\") for its queryable facets, data columns, and supported frequencies.
    Feed the returned facet IDs into the eia connector Mode B \"facets\" config for a general (non-oil-
    preset) EIA pull. Returns the raw v2 metadata unmodified.

    Args:
        route (None | str | Unset): An EIA v2 API route to browse. Omit for the 14 top-level
            routes (e.g. 'electricity', 'petroleum'), pass a top-level route for its child routes, or
            a full leaf dataset route (e.g. 'electricity/retail-sales') for its queryable facets, data
            columns, and supported frequencies -- feed the facet IDs into the eia connector's Mode B
            'facets' config.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            route=route,
        )
    ).parsed
