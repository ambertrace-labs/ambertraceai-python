from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.predict_request import PredictRequest
from ...models.prediction_out import PredictionOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: PredictRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/predict".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> PredictionOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = PredictionOut.from_dict(response.json())

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
) -> Response[PredictionOut | list[ValidationErrorModel]]:
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
    body: PredictRequest,
) -> Response[PredictionOut | list[ValidationErrorModel]]:
    """Run prediction

     Runs the full neurosymbolic prediction pipeline: loads the active trained model, builds features
    from the latest data plus any feature_overrides, generates a point prediction with confidence
    interval, applies symbolic rules (adjustment rules shift the prediction, constraint rules enforce
    hard bounds), and optionally generates an explanation. feature_overrides accepts raw column names
    (e.g. {'FEDFUNDS': 3.0}). For time-series models, overrides are injected into the raw data and
    propagated through engineered features (lags, rolling means). For cross-sectional models, overrides
    directly set input features. The config must have status 'trained'. Returns 409 otherwise.

    Args:
        id (int): Resource ID
        body (PredictRequest): Request body for running a prediction.

            **How feature_overrides work by mode:**

            - **timeseries**: Overrides propagate through lag features. For example,
              ``{"inflation": 5.0}`` sets the latest inflation value, which then
              affects ``inflation_lag_1``, ``inflation_rolling_mean_3``, etc.
              Useful for what-if analysis ("what if inflation hits 5%?").

            - **cross_sectional**: Overrides ARE the input row. Each key-value pair
              maps directly to a model feature. For example,
              ``{"credit_score": 720, "debt_to_income": 0.35}`` provides the exact
              feature values for prediction. You should supply all feature_fields
              defined in the config for best results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PredictionOut | list[ValidationErrorModel]]
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
    body: PredictRequest,
) -> PredictionOut | list[ValidationErrorModel] | None:
    """Run prediction

     Runs the full neurosymbolic prediction pipeline: loads the active trained model, builds features
    from the latest data plus any feature_overrides, generates a point prediction with confidence
    interval, applies symbolic rules (adjustment rules shift the prediction, constraint rules enforce
    hard bounds), and optionally generates an explanation. feature_overrides accepts raw column names
    (e.g. {'FEDFUNDS': 3.0}). For time-series models, overrides are injected into the raw data and
    propagated through engineered features (lags, rolling means). For cross-sectional models, overrides
    directly set input features. The config must have status 'trained'. Returns 409 otherwise.

    Args:
        id (int): Resource ID
        body (PredictRequest): Request body for running a prediction.

            **How feature_overrides work by mode:**

            - **timeseries**: Overrides propagate through lag features. For example,
              ``{"inflation": 5.0}`` sets the latest inflation value, which then
              affects ``inflation_lag_1``, ``inflation_rolling_mean_3``, etc.
              Useful for what-if analysis ("what if inflation hits 5%?").

            - **cross_sectional**: Overrides ARE the input row. Each key-value pair
              maps directly to a model feature. For example,
              ``{"credit_score": 720, "debt_to_income": 0.35}`` provides the exact
              feature values for prediction. You should supply all feature_fields
              defined in the config for best results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PredictionOut | list[ValidationErrorModel]
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
    body: PredictRequest,
) -> Response[PredictionOut | list[ValidationErrorModel]]:
    """Run prediction

     Runs the full neurosymbolic prediction pipeline: loads the active trained model, builds features
    from the latest data plus any feature_overrides, generates a point prediction with confidence
    interval, applies symbolic rules (adjustment rules shift the prediction, constraint rules enforce
    hard bounds), and optionally generates an explanation. feature_overrides accepts raw column names
    (e.g. {'FEDFUNDS': 3.0}). For time-series models, overrides are injected into the raw data and
    propagated through engineered features (lags, rolling means). For cross-sectional models, overrides
    directly set input features. The config must have status 'trained'. Returns 409 otherwise.

    Args:
        id (int): Resource ID
        body (PredictRequest): Request body for running a prediction.

            **How feature_overrides work by mode:**

            - **timeseries**: Overrides propagate through lag features. For example,
              ``{"inflation": 5.0}`` sets the latest inflation value, which then
              affects ``inflation_lag_1``, ``inflation_rolling_mean_3``, etc.
              Useful for what-if analysis ("what if inflation hits 5%?").

            - **cross_sectional**: Overrides ARE the input row. Each key-value pair
              maps directly to a model feature. For example,
              ``{"credit_score": 720, "debt_to_income": 0.35}`` provides the exact
              feature values for prediction. You should supply all feature_fields
              defined in the config for best results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[PredictionOut | list[ValidationErrorModel]]
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
    body: PredictRequest,
) -> PredictionOut | list[ValidationErrorModel] | None:
    """Run prediction

     Runs the full neurosymbolic prediction pipeline: loads the active trained model, builds features
    from the latest data plus any feature_overrides, generates a point prediction with confidence
    interval, applies symbolic rules (adjustment rules shift the prediction, constraint rules enforce
    hard bounds), and optionally generates an explanation. feature_overrides accepts raw column names
    (e.g. {'FEDFUNDS': 3.0}). For time-series models, overrides are injected into the raw data and
    propagated through engineered features (lags, rolling means). For cross-sectional models, overrides
    directly set input features. The config must have status 'trained'. Returns 409 otherwise.

    Args:
        id (int): Resource ID
        body (PredictRequest): Request body for running a prediction.

            **How feature_overrides work by mode:**

            - **timeseries**: Overrides propagate through lag features. For example,
              ``{"inflation": 5.0}`` sets the latest inflation value, which then
              affects ``inflation_lag_1``, ``inflation_rolling_mean_3``, etc.
              Useful for what-if analysis ("what if inflation hits 5%?").

            - **cross_sectional**: Overrides ARE the input row. Each key-value pair
              maps directly to a model feature. For example,
              ``{"credit_score": 720, "debt_to_income": 0.35}`` provides the exact
              feature values for prediction. You should supply all feature_fields
              defined in the config for best results.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        PredictionOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
