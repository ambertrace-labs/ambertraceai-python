from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.prediction_config_create import PredictionConfigCreate
from ...models.prediction_config_out import PredictionConfigOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: PredictionConfigCreate,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/prediction-configs".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PredictionConfigOut | list[ValidationErrorModel] | None:
    if response.status_code == 201:
        response_201 = PredictionConfigOut.from_dict(response.json())

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
) -> Response[PredictionConfigOut | list[ValidationErrorModel]]:
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
    body: PredictionConfigCreate,
) -> Response[PredictionConfigOut | list[ValidationErrorModel]]:
    """Create prediction config

     Creates a prediction configuration defining what to predict and how. Two modes are supported:
    timeseries (forecasts future values from temporally ordered data, requires
    time_index_field/horizon/frequency) and cross_sectional (predicts a target from independent
    observations, omit time fields). After creation, call the train endpoint to fit a model before
    predicting.

    Args:
        id (int): Resource ID
        body (PredictionConfigCreate): Create a prediction configuration for a platform.

            A prediction config defines **what** to predict (``target_field``),
            **how** to predict it (``model_type``, ``feature_fields``), and in
            which **mode** (``timeseries`` or ``cross_sectional``).

            **Choosing a mode:**

            - Use ``timeseries`` when your data has temporal ordering and you want
              to forecast future values (e.g. monthly bond yields, daily stock
              prices, quarterly revenue).  You must supply ``time_index_field``.
            - Use ``cross_sectional`` when each row is an independent observation
              and you want to predict a target from features (e.g. loan approval
              probability, fraud score, patient risk).  Omit ``time_index_field``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PredictionConfigOut | list[ValidationErrorModel]]
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
    body: PredictionConfigCreate,
) -> PredictionConfigOut | list[ValidationErrorModel] | None:
    """Create prediction config

     Creates a prediction configuration defining what to predict and how. Two modes are supported:
    timeseries (forecasts future values from temporally ordered data, requires
    time_index_field/horizon/frequency) and cross_sectional (predicts a target from independent
    observations, omit time fields). After creation, call the train endpoint to fit a model before
    predicting.

    Args:
        id (int): Resource ID
        body (PredictionConfigCreate): Create a prediction configuration for a platform.

            A prediction config defines **what** to predict (``target_field``),
            **how** to predict it (``model_type``, ``feature_fields``), and in
            which **mode** (``timeseries`` or ``cross_sectional``).

            **Choosing a mode:**

            - Use ``timeseries`` when your data has temporal ordering and you want
              to forecast future values (e.g. monthly bond yields, daily stock
              prices, quarterly revenue).  You must supply ``time_index_field``.
            - Use ``cross_sectional`` when each row is an independent observation
              and you want to predict a target from features (e.g. loan approval
              probability, fraud score, patient risk).  Omit ``time_index_field``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PredictionConfigOut | list[ValidationErrorModel]
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
    body: PredictionConfigCreate,
) -> Response[PredictionConfigOut | list[ValidationErrorModel]]:
    """Create prediction config

     Creates a prediction configuration defining what to predict and how. Two modes are supported:
    timeseries (forecasts future values from temporally ordered data, requires
    time_index_field/horizon/frequency) and cross_sectional (predicts a target from independent
    observations, omit time fields). After creation, call the train endpoint to fit a model before
    predicting.

    Args:
        id (int): Resource ID
        body (PredictionConfigCreate): Create a prediction configuration for a platform.

            A prediction config defines **what** to predict (``target_field``),
            **how** to predict it (``model_type``, ``feature_fields``), and in
            which **mode** (``timeseries`` or ``cross_sectional``).

            **Choosing a mode:**

            - Use ``timeseries`` when your data has temporal ordering and you want
              to forecast future values (e.g. monthly bond yields, daily stock
              prices, quarterly revenue).  You must supply ``time_index_field``.
            - Use ``cross_sectional`` when each row is an independent observation
              and you want to predict a target from features (e.g. loan approval
              probability, fraud score, patient risk).  Omit ``time_index_field``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PredictionConfigOut | list[ValidationErrorModel]]
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
    body: PredictionConfigCreate,
) -> PredictionConfigOut | list[ValidationErrorModel] | None:
    """Create prediction config

     Creates a prediction configuration defining what to predict and how. Two modes are supported:
    timeseries (forecasts future values from temporally ordered data, requires
    time_index_field/horizon/frequency) and cross_sectional (predicts a target from independent
    observations, omit time fields). After creation, call the train endpoint to fit a model before
    predicting.

    Args:
        id (int): Resource ID
        body (PredictionConfigCreate): Create a prediction configuration for a platform.

            A prediction config defines **what** to predict (``target_field``),
            **how** to predict it (``model_type``, ``feature_fields``), and in
            which **mode** (``timeseries`` or ``cross_sectional``).

            **Choosing a mode:**

            - Use ``timeseries`` when your data has temporal ordering and you want
              to forecast future values (e.g. monthly bond yields, daily stock
              prices, quarterly revenue).  You must supply ``time_index_field``.
            - Use ``cross_sectional`` when each row is an independent observation
              and you want to predict a target from features (e.g. loan approval
              probability, fraud score, patient risk).  Omit ``time_index_field``.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PredictionConfigOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
