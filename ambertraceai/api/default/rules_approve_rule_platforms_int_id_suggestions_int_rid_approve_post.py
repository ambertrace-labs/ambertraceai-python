from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.approve_request import ApproveRequest
from ...models.suggestion_out import SuggestionOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    rid: int,
    *,
    body: ApproveRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/suggestions/{rid}/approve".format(
            id=quote(str(id), safe=""),
            rid=quote(str(rid), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> SuggestionOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = SuggestionOut.from_dict(response.json())

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
) -> Response[SuggestionOut | list[ValidationErrorModel]]:
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
    body: ApproveRequest,
) -> Response[SuggestionOut | list[ValidationErrorModel]]:
    """Approve rule suggestion

     Approves a suggested rule, making it active for future queries. Optionally include a reason for the
    approval decision.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID
        body (ApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuggestionOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        rid=rid,
        body=body,
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
    body: ApproveRequest,
) -> SuggestionOut | list[ValidationErrorModel] | None:
    """Approve rule suggestion

     Approves a suggested rule, making it active for future queries. Optionally include a reason for the
    approval decision.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID
        body (ApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuggestionOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        rid=rid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveRequest,
) -> Response[SuggestionOut | list[ValidationErrorModel]]:
    """Approve rule suggestion

     Approves a suggested rule, making it active for future queries. Optionally include a reason for the
    approval decision.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID
        body (ApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[SuggestionOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        rid=rid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    rid: int,
    *,
    client: AuthenticatedClient | Client,
    body: ApproveRequest,
) -> SuggestionOut | list[ValidationErrorModel] | None:
    """Approve rule suggestion

     Approves a suggested rule, making it active for future queries. Optionally include a reason for the
    approval decision.

    Args:
        id (int): Platform ID
        rid (int): Rule/suggestion ID
        body (ApproveRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        SuggestionOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            rid=rid,
            client=client,
            body=body,
        )
    ).parsed
