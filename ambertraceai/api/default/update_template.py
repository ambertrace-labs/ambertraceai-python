from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.template_out import TemplateOut
from ...models.template_update import TemplateUpdate
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    tid: int,
    *,
    body: TemplateUpdate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "put",
        "url": "/api/v1/domains/{id}/templates/{tid}".format(
            id=quote(str(id), safe=""),
            tid=quote(str(tid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> TemplateOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = TemplateOut.from_dict(response.json())

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
) -> Response[TemplateOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    tid: int,
    *,
    client: AuthenticatedClient | Client,
    body: TemplateUpdate,
) -> Response[TemplateOut | list[ValidationErrorModel]]:
    """Update rule template

     Updates a rule template. Only non-null fields are changed.

    Args:
        id (int): Domain ID
        tid (int): Template ID
        body (TemplateUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TemplateOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        tid=tid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    tid: int,
    *,
    client: AuthenticatedClient | Client,
    body: TemplateUpdate,
) -> TemplateOut | list[ValidationErrorModel] | None:
    """Update rule template

     Updates a rule template. Only non-null fields are changed.

    Args:
        id (int): Domain ID
        tid (int): Template ID
        body (TemplateUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TemplateOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        tid=tid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    tid: int,
    *,
    client: AuthenticatedClient | Client,
    body: TemplateUpdate,
) -> Response[TemplateOut | list[ValidationErrorModel]]:
    """Update rule template

     Updates a rule template. Only non-null fields are changed.

    Args:
        id (int): Domain ID
        tid (int): Template ID
        body (TemplateUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[TemplateOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        tid=tid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    tid: int,
    *,
    client: AuthenticatedClient | Client,
    body: TemplateUpdate,
) -> TemplateOut | list[ValidationErrorModel] | None:
    """Update rule template

     Updates a rule template. Only non-null fields are changed.

    Args:
        id (int): Domain ID
        tid (int): Template ID
        body (TemplateUpdate):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        TemplateOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            tid=tid,
            client=client,
            body=body,
        )
    ).parsed
