from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.eval_config_suggest_request import EvalConfigSuggestRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: EvalConfigSuggestRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/domains/{id}/eval-config/suggest".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
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
    body: EvalConfigSuggestRequest,
) -> Response[list[ValidationErrorModel]]:
    """Suggest eval configs

     Uses LLM to suggest evaluation configurations based on the domain's ontology. Returns 202 and runs
    asynchronously. Specify n_options (1-5) to control how many alternatives are generated.

    Args:
        id (int): Resource ID
        body (EvalConfigSuggestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
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
    body: EvalConfigSuggestRequest,
) -> list[ValidationErrorModel] | None:
    """Suggest eval configs

     Uses LLM to suggest evaluation configurations based on the domain's ontology. Returns 202 and runs
    asynchronously. Specify n_options (1-5) to control how many alternatives are generated.

    Args:
        id (int): Resource ID
        body (EvalConfigSuggestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
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
    body: EvalConfigSuggestRequest,
) -> Response[list[ValidationErrorModel]]:
    """Suggest eval configs

     Uses LLM to suggest evaluation configurations based on the domain's ontology. Returns 202 and runs
    asynchronously. Specify n_options (1-5) to control how many alternatives are generated.

    Args:
        id (int): Resource ID
        body (EvalConfigSuggestRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
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
    body: EvalConfigSuggestRequest,
) -> list[ValidationErrorModel] | None:
    """Suggest eval configs

     Uses LLM to suggest evaluation configurations based on the domain's ontology. Returns 202 and runs
    asynchronously. Specify n_options (1-5) to control how many alternatives are generated.

    Args:
        id (int): Resource ID
        body (EvalConfigSuggestRequest):

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
            body=body,
        )
    ).parsed
