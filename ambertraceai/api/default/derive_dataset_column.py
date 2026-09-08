from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.dataset_derive_request import DatasetDeriveRequest
from ...models.dataset_out import DatasetOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: DatasetDeriveRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/datasets/{id}/derive".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> DatasetOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = DatasetOut.from_dict(response.json())

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
) -> Response[DatasetOut | list[ValidationErrorModel]]:
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
    body: DatasetDeriveRequest,
) -> Response[DatasetOut | list[ValidationErrorModel]]:
    """Derive an arithmetic column

     Computes ONE new column as a fixed binary arithmetic expression over TWO existing columns
    (subtract/add/multiply/divide) and materialises it into the dataset file + schema_info -- the
    derived column then resolves as create_config(target_field=...) AND is auto-included as a driver-
    discovery candidate, with no other API/prediction-pipeline change. Synchronous (pure CPU, no
    network): returns 200 with the updated dataset immediately, no polling. NaN propagates when either
    operand is missing for a row (never filled -- fail-closed); divide-by-zero yields NaN, never inf.
    409 if new_column already exists; 422 if left/right is not an existing column. drop_source_columns
    (default true) drops the two operand columns AFTER computing -- recommended when the derived column
    is a forecast target, since leaving the legs in the panel makes them mechanically-perfect (and
    therefore uninformative) drivers of their own derivation.

    Args:
        id (int): Resource ID
        body (DatasetDeriveRequest): Derive one new column as a fixed binary arithmetic
            expression.

            v1 grammar (deliberately minimal): exactly ONE op over TWO
            EXISTING named columns -> ONE new named column. No scalars, no chaining,
            no general expression evaluator.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | list[ValidationErrorModel]]
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
    body: DatasetDeriveRequest,
) -> DatasetOut | list[ValidationErrorModel] | None:
    """Derive an arithmetic column

     Computes ONE new column as a fixed binary arithmetic expression over TWO existing columns
    (subtract/add/multiply/divide) and materialises it into the dataset file + schema_info -- the
    derived column then resolves as create_config(target_field=...) AND is auto-included as a driver-
    discovery candidate, with no other API/prediction-pipeline change. Synchronous (pure CPU, no
    network): returns 200 with the updated dataset immediately, no polling. NaN propagates when either
    operand is missing for a row (never filled -- fail-closed); divide-by-zero yields NaN, never inf.
    409 if new_column already exists; 422 if left/right is not an existing column. drop_source_columns
    (default true) drops the two operand columns AFTER computing -- recommended when the derived column
    is a forecast target, since leaving the legs in the panel makes them mechanically-perfect (and
    therefore uninformative) drivers of their own derivation.

    Args:
        id (int): Resource ID
        body (DatasetDeriveRequest): Derive one new column as a fixed binary arithmetic
            expression.

            v1 grammar (deliberately minimal): exactly ONE op over TWO
            EXISTING named columns -> ONE new named column. No scalars, no chaining,
            no general expression evaluator.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | list[ValidationErrorModel]
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
    body: DatasetDeriveRequest,
) -> Response[DatasetOut | list[ValidationErrorModel]]:
    """Derive an arithmetic column

     Computes ONE new column as a fixed binary arithmetic expression over TWO existing columns
    (subtract/add/multiply/divide) and materialises it into the dataset file + schema_info -- the
    derived column then resolves as create_config(target_field=...) AND is auto-included as a driver-
    discovery candidate, with no other API/prediction-pipeline change. Synchronous (pure CPU, no
    network): returns 200 with the updated dataset immediately, no polling. NaN propagates when either
    operand is missing for a row (never filled -- fail-closed); divide-by-zero yields NaN, never inf.
    409 if new_column already exists; 422 if left/right is not an existing column. drop_source_columns
    (default true) drops the two operand columns AFTER computing -- recommended when the derived column
    is a forecast target, since leaving the legs in the panel makes them mechanically-perfect (and
    therefore uninformative) drivers of their own derivation.

    Args:
        id (int): Resource ID
        body (DatasetDeriveRequest): Derive one new column as a fixed binary arithmetic
            expression.

            v1 grammar (deliberately minimal): exactly ONE op over TWO
            EXISTING named columns -> ONE new named column. No scalars, no chaining,
            no general expression evaluator.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[DatasetOut | list[ValidationErrorModel]]
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
    body: DatasetDeriveRequest,
) -> DatasetOut | list[ValidationErrorModel] | None:
    """Derive an arithmetic column

     Computes ONE new column as a fixed binary arithmetic expression over TWO existing columns
    (subtract/add/multiply/divide) and materialises it into the dataset file + schema_info -- the
    derived column then resolves as create_config(target_field=...) AND is auto-included as a driver-
    discovery candidate, with no other API/prediction-pipeline change. Synchronous (pure CPU, no
    network): returns 200 with the updated dataset immediately, no polling. NaN propagates when either
    operand is missing for a row (never filled -- fail-closed); divide-by-zero yields NaN, never inf.
    409 if new_column already exists; 422 if left/right is not an existing column. drop_source_columns
    (default true) drops the two operand columns AFTER computing -- recommended when the derived column
    is a forecast target, since leaving the legs in the panel makes them mechanically-perfect (and
    therefore uninformative) drivers of their own derivation.

    Args:
        id (int): Resource ID
        body (DatasetDeriveRequest): Derive one new column as a fixed binary arithmetic
            expression.

            v1 grammar (deliberately minimal): exactly ONE op over TWO
            EXISTING named columns -> ONE new named column. No scalars, no chaining,
            no general expression evaluator.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        DatasetOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
