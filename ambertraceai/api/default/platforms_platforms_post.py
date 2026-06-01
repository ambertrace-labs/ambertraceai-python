from http import HTTPStatus
from typing import Any

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.build_request import BuildRequest
from ...models.platform_out import PlatformOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    *,
    body: BuildRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms",
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PlatformOut | list[ValidationErrorModel] | None:
    if response.status_code == 202:
        response_202 = PlatformOut.from_dict(response.json())

        return response_202

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
    *,
    client: AuthenticatedClient | Client,
    body: BuildRequest,
) -> Response[PlatformOut | list[ValidationErrorModel]]:
    """Build platform

     Builds a neurosymbolic platform from a domain and its datasets. Returns 202 with a job ID. The build
    process creates a knowledge graph, compiles ontology constraints into symbolic rules, and prepares
    the platform for queries and predictions. Poll GET /jobs/{id} until status is 'ready'. The domain
    must have status 'active' and at least one entity defined.

    Args:
        body (BuildRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PlatformOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: AuthenticatedClient | Client,
    body: BuildRequest,
) -> PlatformOut | list[ValidationErrorModel] | None:
    """Build platform

     Builds a neurosymbolic platform from a domain and its datasets. Returns 202 with a job ID. The build
    process creates a knowledge graph, compiles ontology constraints into symbolic rules, and prepares
    the platform for queries and predictions. Poll GET /jobs/{id} until status is 'ready'. The domain
    must have status 'active' and at least one entity defined.

    Args:
        body (BuildRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PlatformOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    *,
    client: AuthenticatedClient | Client,
    body: BuildRequest,
) -> Response[PlatformOut | list[ValidationErrorModel]]:
    """Build platform

     Builds a neurosymbolic platform from a domain and its datasets. Returns 202 with a job ID. The build
    process creates a knowledge graph, compiles ontology constraints into symbolic rules, and prepares
    the platform for queries and predictions. Poll GET /jobs/{id} until status is 'ready'. The domain
    must have status 'active' and at least one entity defined.

    Args:
        body (BuildRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PlatformOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: AuthenticatedClient | Client,
    body: BuildRequest,
) -> PlatformOut | list[ValidationErrorModel] | None:
    """Build platform

     Builds a neurosymbolic platform from a domain and its datasets. Returns 202 with a job ID. The build
    process creates a knowledge graph, compiles ontology constraints into symbolic rules, and prepares
    the platform for queries and predictions. Poll GET /jobs/{id} until status is 'ready'. The domain
    must have status 'active' and at least one entity defined.

    Args:
        body (BuildRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PlatformOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
        )
    ).parsed
