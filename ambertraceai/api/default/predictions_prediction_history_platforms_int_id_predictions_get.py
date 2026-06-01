from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.forecast_out import ForecastOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import UNSET, Response, Unset


def _get_kwargs(
    id: int,
    *,
    prediction_config_id: int,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> dict[str, Any]:

    params: dict[str, Any] = {}

    params["prediction_config_id"] = prediction_config_id

    params["limit"] = limit

    params["offset"] = offset

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/platforms/{id}/predictions".format(
            id=quote(str(id), safe=""),
        ),
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ForecastOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = ForecastOut.from_dict(response.json())

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
) -> Response[ForecastOut | list[ValidationErrorModel]]:
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
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[ForecastOut | list[ValidationErrorModel]]:
    """Get prediction history

     Returns stored forecast records for a specific prediction config, ordered by creation time (most
    recent first). Each record includes the predicted value, confidence interval, features used, and any
    symbolic rule adjustments applied. For timeseries configs, forecast_date indicates the predicted
    date. For cross_sectional configs, it reflects the prediction creation time. Use actual_value
    (backfilled when ground truth becomes available) to track accuracy.

    Args:
        id (int): Resource ID
        prediction_config_id (int): Filter history to this prediction config.
        limit (int | Unset): Maximum number of records to return. Default: 100.
        offset (int | Unset): Number of records to skip for pagination. Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ForecastOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        prediction_config_id=prediction_config_id,
        limit=limit,
        offset=offset,
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
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> ForecastOut | list[ValidationErrorModel] | None:
    """Get prediction history

     Returns stored forecast records for a specific prediction config, ordered by creation time (most
    recent first). Each record includes the predicted value, confidence interval, features used, and any
    symbolic rule adjustments applied. For timeseries configs, forecast_date indicates the predicted
    date. For cross_sectional configs, it reflects the prediction creation time. Use actual_value
    (backfilled when ground truth becomes available) to track accuracy.

    Args:
        id (int): Resource ID
        prediction_config_id (int): Filter history to this prediction config.
        limit (int | Unset): Maximum number of records to return. Default: 100.
        offset (int | Unset): Number of records to skip for pagination. Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ForecastOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        client=client,
        prediction_config_id=prediction_config_id,
        limit=limit,
        offset=offset,
    ).parsed


async def asyncio_detailed(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> Response[ForecastOut | list[ValidationErrorModel]]:
    """Get prediction history

     Returns stored forecast records for a specific prediction config, ordered by creation time (most
    recent first). Each record includes the predicted value, confidence interval, features used, and any
    symbolic rule adjustments applied. For timeseries configs, forecast_date indicates the predicted
    date. For cross_sectional configs, it reflects the prediction creation time. Use actual_value
    (backfilled when ground truth becomes available) to track accuracy.

    Args:
        id (int): Resource ID
        prediction_config_id (int): Filter history to this prediction config.
        limit (int | Unset): Maximum number of records to return. Default: 100.
        offset (int | Unset): Number of records to skip for pagination. Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ForecastOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        prediction_config_id=prediction_config_id,
        limit=limit,
        offset=offset,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    *,
    client: AuthenticatedClient | Client,
    prediction_config_id: int,
    limit: int | Unset = 100,
    offset: int | Unset = 0,
) -> ForecastOut | list[ValidationErrorModel] | None:
    """Get prediction history

     Returns stored forecast records for a specific prediction config, ordered by creation time (most
    recent first). Each record includes the predicted value, confidence interval, features used, and any
    symbolic rule adjustments applied. For timeseries configs, forecast_date indicates the predicted
    date. For cross_sectional configs, it reflects the prediction creation time. Use actual_value
    (backfilled when ground truth becomes available) to track accuracy.

    Args:
        id (int): Resource ID
        prediction_config_id (int): Filter history to this prediction config.
        limit (int | Unset): Maximum number of records to return. Default: 100.
        offset (int | Unset): Number of records to skip for pagination. Default: 0.

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ForecastOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            prediction_config_id=prediction_config_id,
            limit=limit,
            offset=offset,
        )
    ).parsed
