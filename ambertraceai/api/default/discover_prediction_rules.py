from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.discover_prediction_rules_request import DiscoverPredictionRulesRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: DiscoverPredictionRulesRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/discover-prediction-rules".format(
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
    body: DiscoverPredictionRulesRequest,
) -> Response[list[ValidationErrorModel]]:
    """Discover prediction rules

     Starts async neurosymbolic rule discovery for a trained prediction config. Analyses the model
    residuals, proposes corrective adjustment/constraint rule candidates (template + LLM), and A/B-tests
    each against the expanding-window backtest. Accepted rules are stored pending expert approval
    (is_active=false). Returns 202 with a job_id — poll GET /api/v1/jobs/{job_id} for the
    accepted/rejected summary, then GET /platforms/{id}/discovered-prediction-rules to retrieve the
    rules with their per-rule fire_rate and backtest delta.

    Args:
        id (int): Resource ID
        body (DiscoverPredictionRulesRequest): Request body for triggering prediction rule
            discovery.

            Discovery analyses the trained model's residuals, generates corrective rule
            candidates (template-driven + LLM-parameterised), and A/B tests each against
            the expanding-window backtest. Accepted rules are stored pending expert
            approval (``is_active=False``). Runs in the background — the route returns 202.

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
    body: DiscoverPredictionRulesRequest,
) -> list[ValidationErrorModel] | None:
    """Discover prediction rules

     Starts async neurosymbolic rule discovery for a trained prediction config. Analyses the model
    residuals, proposes corrective adjustment/constraint rule candidates (template + LLM), and A/B-tests
    each against the expanding-window backtest. Accepted rules are stored pending expert approval
    (is_active=false). Returns 202 with a job_id — poll GET /api/v1/jobs/{job_id} for the
    accepted/rejected summary, then GET /platforms/{id}/discovered-prediction-rules to retrieve the
    rules with their per-rule fire_rate and backtest delta.

    Args:
        id (int): Resource ID
        body (DiscoverPredictionRulesRequest): Request body for triggering prediction rule
            discovery.

            Discovery analyses the trained model's residuals, generates corrective rule
            candidates (template-driven + LLM-parameterised), and A/B tests each against
            the expanding-window backtest. Accepted rules are stored pending expert
            approval (``is_active=False``). Runs in the background — the route returns 202.

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
    body: DiscoverPredictionRulesRequest,
) -> Response[list[ValidationErrorModel]]:
    """Discover prediction rules

     Starts async neurosymbolic rule discovery for a trained prediction config. Analyses the model
    residuals, proposes corrective adjustment/constraint rule candidates (template + LLM), and A/B-tests
    each against the expanding-window backtest. Accepted rules are stored pending expert approval
    (is_active=false). Returns 202 with a job_id — poll GET /api/v1/jobs/{job_id} for the
    accepted/rejected summary, then GET /platforms/{id}/discovered-prediction-rules to retrieve the
    rules with their per-rule fire_rate and backtest delta.

    Args:
        id (int): Resource ID
        body (DiscoverPredictionRulesRequest): Request body for triggering prediction rule
            discovery.

            Discovery analyses the trained model's residuals, generates corrective rule
            candidates (template-driven + LLM-parameterised), and A/B tests each against
            the expanding-window backtest. Accepted rules are stored pending expert
            approval (``is_active=False``). Runs in the background — the route returns 202.

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
    body: DiscoverPredictionRulesRequest,
) -> list[ValidationErrorModel] | None:
    """Discover prediction rules

     Starts async neurosymbolic rule discovery for a trained prediction config. Analyses the model
    residuals, proposes corrective adjustment/constraint rule candidates (template + LLM), and A/B-tests
    each against the expanding-window backtest. Accepted rules are stored pending expert approval
    (is_active=false). Returns 202 with a job_id — poll GET /api/v1/jobs/{job_id} for the
    accepted/rejected summary, then GET /platforms/{id}/discovered-prediction-rules to retrieve the
    rules with their per-rule fire_rate and backtest delta.

    Args:
        id (int): Resource ID
        body (DiscoverPredictionRulesRequest): Request body for triggering prediction rule
            discovery.

            Discovery analyses the trained model's residuals, generates corrective rule
            candidates (template-driven + LLM-parameterised), and A/B tests each against
            the expanding-window backtest. Accepted rules are stored pending expert
            approval (``is_active=False``). Runs in the background — the route returns 202.

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
