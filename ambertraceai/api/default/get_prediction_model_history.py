from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.model_version_out import ModelVersionOut
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    cid: int,
) -> dict[str, Any]:

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/api/v1/platforms/{id}/prediction-configs/{cid}/model-history".format(
            id=quote(str(id), safe=""),
            cid=quote(str(cid), safe=""),
        ),
    }

    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> ModelVersionOut | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = ModelVersionOut.from_dict(response.json())

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
) -> Response[ModelVersionOut | list[ValidationErrorModel]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ModelVersionOut | list[ValidationErrorModel]]:
    r"""List every trained model version of a prediction config

     Returns every model version trained for the config, newest first, each with its `model_version`,
    evaluation metrics, `dataset_ids` and `dataset_fingerprint` (the training data it used),
    `trained_at`, and whether it is the active version. Retraining adds a version and never overwrites
    an earlier one, so this answers \"which model, trained on which data, was serving then\". Reads
    metadata only; no model is loaded. Returns an empty list when the config has never been trained.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModelVersionOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        cid=cid,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> ModelVersionOut | list[ValidationErrorModel] | None:
    r"""List every trained model version of a prediction config

     Returns every model version trained for the config, newest first, each with its `model_version`,
    evaluation metrics, `dataset_ids` and `dataset_fingerprint` (the training data it used),
    `trained_at`, and whether it is the active version. Retraining adds a version and never overwrites
    an earlier one, so this answers \"which model, trained on which data, was serving then\". Reads
    metadata only; no model is loaded. Returns an empty list when the config has never been trained.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ModelVersionOut | list[ValidationErrorModel]
    """

    return sync_detailed(
        id=id,
        cid=cid,
        client=client,
    ).parsed


async def asyncio_detailed(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> Response[ModelVersionOut | list[ValidationErrorModel]]:
    r"""List every trained model version of a prediction config

     Returns every model version trained for the config, newest first, each with its `model_version`,
    evaluation metrics, `dataset_ids` and `dataset_fingerprint` (the training data it used),
    `trained_at`, and whether it is the active version. Retraining adds a version and never overwrites
    an earlier one, so this answers \"which model, trained on which data, was serving then\". Reads
    metadata only; no model is loaded. Returns an empty list when the config has never been trained.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[ModelVersionOut | list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        id=id,
        cid=cid,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    id: int,
    cid: int,
    *,
    client: AuthenticatedClient | Client,
) -> ModelVersionOut | list[ValidationErrorModel] | None:
    r"""List every trained model version of a prediction config

     Returns every model version trained for the config, newest first, each with its `model_version`,
    evaluation metrics, `dataset_ids` and `dataset_fingerprint` (the training data it used),
    `trained_at`, and whether it is the active version. Retraining adds a version and never overwrites
    an earlier one, so this answers \"which model, trained on which data, was serving then\". Reads
    metadata only; no model is loaded. Returns an empty list when the config has never been trained.

    Args:
        id (int): Platform ID
        cid (int): Prediction config ID

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        ModelVersionOut | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            cid=cid,
            client=client,
        )
    ).parsed
