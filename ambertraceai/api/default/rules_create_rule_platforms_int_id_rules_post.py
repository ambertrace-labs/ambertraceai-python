from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.rule_create_request import RuleCreateRequest
from ...models.rule_out import RuleOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: RuleCreateRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/rules".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> RuleOut | list[ValidationErrorModel] | None:
    if response.status_code == 201:
        response_201 = RuleOut.from_dict(response.json())

        return response_201

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
    body: RuleCreateRequest,
) -> Response[RuleOut | list[ValidationErrorModel]]:
    """Create rule

     Creates a symbolic rule manually on a platform. The rule structure is validated (operators, action
    type/value, logical consistency against the existing active rules); structurally invalid rules are
    rejected with 422. On a verified-profile platform an active rule must also pass the verified gate
    (grammar lock + stratification + invariant manifest over the prospective active set) — if it would
    make the set unsafe the request is rejected with 409 naming the reasons. Returns 201 with the
    created rule.

    Args:
        id (int): Resource ID
        body (RuleCreateRequest): Create an active or pending symbolic rule manually.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RuleCreateRequest,
) -> RuleOut | list[ValidationErrorModel] | None:
    """Create rule

     Creates a symbolic rule manually on a platform. The rule structure is validated (operators, action
    type/value, logical consistency against the existing active rules); structurally invalid rules are
    rejected with 422. On a verified-profile platform an active rule must also pass the verified gate
    (grammar lock + stratification + invariant manifest over the prospective active set) — if it would
    make the set unsafe the request is rejected with 409 naming the reasons. Returns 201 with the
    created rule.

    Args:
        id (int): Resource ID
        body (RuleCreateRequest): Create an active or pending symbolic rule manually.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        RuleOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RuleCreateRequest,
) -> Response[RuleOut | list[ValidationErrorModel]]:
    """Create rule

     Creates a symbolic rule manually on a platform. The rule structure is validated (operators, action
    type/value, logical consistency against the existing active rules); structurally invalid rules are
    rejected with 422. On a verified-profile platform an active rule must also pass the verified gate
    (grammar lock + stratification + invariant manifest over the prospective active set) — if it would
    make the set unsafe the request is rejected with 409 naming the reasons. Returns 201 with the
    created rule.

    Args:
        id (int): Resource ID
        body (RuleCreateRequest): Create an active or pending symbolic rule manually.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[RuleOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    body: RuleCreateRequest,
) -> RuleOut | list[ValidationErrorModel] | None:
    """Create rule

     Creates a symbolic rule manually on a platform. The rule structure is validated (operators, action
    type/value, logical consistency against the existing active rules); structurally invalid rules are
    rejected with 422. On a verified-profile platform an active rule must also pass the verified gate
    (grammar lock + stratification + invariant manifest over the prospective active set) — if it would
    make the set unsafe the request is rejected with 409 naming the reasons. Returns 201 with the
    created rule.

    Args:
        id (int): Resource ID
        body (RuleCreateRequest): Create an active or pending symbolic rule manually.

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
            body=body,
        )
    ).parsed
