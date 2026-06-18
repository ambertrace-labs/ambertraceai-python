from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/domains/{id}/build-ontology".format(
            id=quote(str(id), safe=""),
        ),
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
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[ValidationErrorModel]]:
    """Build ontology

     Generates entities, relationships, and constraints from the domain description, authored against the
    columns of the attached dataset. A dataset is REQUIRED: upload data to the domain first (returns 400
    otherwise). Rules are written against the real column vocabulary, and every field reference is
    validated to map to a column or an in-set derived head at creation time (a schema_reconciliation
    report is recorded; an unmappable reference fails the build rather than producing a dead rule).
    Returns 202 with a job id -- poll GET /jobs/{job_id} until status is 'completed' (success) or
    'failed'. The domain status also moves from 'building' to 'active' (success) or the terminal 'error'
    (failure); on failure the job's error_message carries an actionable reason. The generated
    constraints become executable symbolic rules automatically when a platform is built.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> list[ValidationErrorModel] | None:
    """Build ontology

     Generates entities, relationships, and constraints from the domain description, authored against the
    columns of the attached dataset. A dataset is REQUIRED: upload data to the domain first (returns 400
    otherwise). Rules are written against the real column vocabulary, and every field reference is
    validated to map to a column or an in-set derived head at creation time (a schema_reconciliation
    report is recorded; an unmappable reference fails the build rather than producing a dead rule).
    Returns 202 with a job id -- poll GET /jobs/{job_id} until status is 'completed' (success) or
    'failed'. The domain status also moves from 'building' to 'active' (success) or the terminal 'error'
    (failure); on failure the job's error_message carries an actionable reason. The generated
    constraints become executable symbolic rules automatically when a platform is built.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[list[ValidationErrorModel]]:
    """Build ontology

     Generates entities, relationships, and constraints from the domain description, authored against the
    columns of the attached dataset. A dataset is REQUIRED: upload data to the domain first (returns 400
    otherwise). Rules are written against the real column vocabulary, and every field reference is
    validated to map to a column or an in-set derived head at creation time (a schema_reconciliation
    report is recorded; an unmappable reference fails the build rather than producing a dead rule).
    Returns 202 with a job id -- poll GET /jobs/{job_id} until status is 'completed' (success) or
    'failed'. The domain status also moves from 'building' to 'active' (success) or the terminal 'error'
    (failure); on failure the job's error_message carries an actionable reason. The generated
    constraints become executable symbolic rules automatically when a platform is built.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
) -> list[ValidationErrorModel] | None:
    """Build ontology

     Generates entities, relationships, and constraints from the domain description, authored against the
    columns of the attached dataset. A dataset is REQUIRED: upload data to the domain first (returns 400
    otherwise). Rules are written against the real column vocabulary, and every field reference is
    validated to map to a column or an in-set derived head at creation time (a schema_reconciliation
    report is recorded; an unmappable reference fails the build rather than producing a dead rule).
    Returns 202 with a job id -- poll GET /jobs/{job_id} until status is 'completed' (success) or
    'failed'. The domain status also moves from 'building' to 'active' (success) or the terminal 'error'
    (failure); on failure the job's error_message carries an actionable reason. The generated
    constraints become executable symbolic rules automatically when a platform is built.

    Args:
        id (int): Resource ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
        )
    ).parsed
