from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response


def _get_kwargs(
    id: int,
    *,
    prediction_config_id: int,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["prediction_config_id"] = prediction_config_id

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/platforms/{id}/neurosymbolic-comparison".format(
            id=quote(str(id), safe=""),
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
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
) -> Response[list[ValidationErrorModel]]:
    """Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, fire_rate}. Timeseries configs only.

    Args:
        id (int): Resource ID
        prediction_config_id (int): The timeseries prediction config to compare. Neural metrics
            are computed from the model alone; neurosymbolic metrics apply the platform's active
            adjustment+constraint rules over the same holdout.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        prediction_config_id=prediction_config_id,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
) -> list[ValidationErrorModel] | None:
    """Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, fire_rate}. Timeseries configs only.

    Args:
        id (int): Resource ID
        prediction_config_id (int): The timeseries prediction config to compare. Neural metrics
            are computed from the model alone; neurosymbolic metrics apply the platform's active
            adjustment+constraint rules over the same holdout.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
        prediction_config_id=prediction_config_id,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
) -> Response[list[ValidationErrorModel]]:
    """Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, fire_rate}. Timeseries configs only.

    Args:
        id (int): Resource ID
        prediction_config_id (int): The timeseries prediction config to compare. Neural metrics
            are computed from the model alone; neurosymbolic metrics apply the platform's active
            adjustment+constraint rules over the same holdout.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        prediction_config_id=prediction_config_id,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
) -> list[ValidationErrorModel] | None:
    """Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, fire_rate}. Timeseries configs only.

    Args:
        id (int): Resource ID
        prediction_config_id (int): The timeseries prediction config to compare. Neural metrics
            are computed from the model alone; neurosymbolic metrics apply the platform's active
            adjustment+constraint rules over the same holdout.

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
            prediction_config_id=prediction_config_id,
        )
    ).parsed
