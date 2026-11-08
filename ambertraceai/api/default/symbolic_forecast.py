from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.symbolic_forecast_request import SymbolicForecastRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: SymbolicForecastRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/symbolic-forecast".format(
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
    body: SymbolicForecastRequest,
) -> Response[list[ValidationErrorModel]]:
    r"""Symbolic forecast with a proof-carrying WHY

     Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction config's dataset and
    returns the forecast WITH its WHY: the ordered driver-rules that fired (over the dataset's real
    features), each with its fitted contribution, band, and reliability. forecast = baseline
    (persistence) + Σ fired-driver contributions, so the structure IS the explanation. With
    verified=true the active-driver set is run through the verified kernel — each driver is stamped
    proof_checked and a why_certification block is attached. Magnitudes/bands are statistical (outside
    the proof). Feature-flagged (AMBERTRACE_SYMBOLIC_FORECAST); 404 when disabled. PRECONDITION to serve
    a platform: a prediction config exists on the platform whose target_field is present and numeric in
    at least one ready/ingested dataset. No training and no minimum row count is required — when too few
    rows or too weak a signal yield no driver-rules, the response is an HONEST forecast: with the
    default baseline_mode=neural the value is the GBT prediction through the S2 confidence gate
    (forecast_tier=neural_scored when confident, neural_weak when below threshold, with
    neural_confidence_tau emitted separately — the raw GBT prediction is always served, never replaced;
    no_forecast only when no model exists); with other anchors it is the baseline anchor
    (forecast_tier=baseline_anchor; point_is_persistence==true ONLY when baseline_mode is persistence).
    WITH a real RMSE-based interval, not an error. Unmet preconditions return a STRUCTURED error (409
    when the target is absent from every dataset; 422 when the latest row's target is non-numeric),
    never a raw 404.

    ASYNC: returns 202 immediately with {job_id, poll, status:\"forecasting\"}; the fit runs in the
    background (minutes on wide panels). Poll GET /api/v1/jobs/{job_id} — on completion the job `result`
    IS the forecast payload described above; on failure the job status is failed, `error_message`
    carries the reason and `result.error` the structured {code, message, http_status} (the status the
    former synchronous endpoint returned, e.g. 409 target absent, 422 validation). An identical request
    already in flight returns the existing job_id (deduplicated=true). The 404 (flag off), 403 and
    config-not-found errors are still returned synchronously. Requires a user or session credential
    (platform-scoped keys get 403), since the job is polled via GET /jobs/{id}.

    Capability gating: requires the \"predictions\" capability (see GET /api/v1/capabilities). Returns
    403 capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (SymbolicForecastRequest): Request body for the symbolic-forecast "why" endpoint.

            Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction
            config's dataset: it induces human-readable driver-rules over the dataset's
            REAL features and composes the forecast as ``baseline + Σ fired drivers``, so
            the response carries an actionable *why* (the ordered drivers + their fitted
            contributions + reliability), not just a number. With ``verified=true`` the
            active-driver set is run through the verified kernel and each driver is
            stamped ``proof_checked``.

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
    body: SymbolicForecastRequest,
) -> list[ValidationErrorModel] | None:
    r"""Symbolic forecast with a proof-carrying WHY

     Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction config's dataset and
    returns the forecast WITH its WHY: the ordered driver-rules that fired (over the dataset's real
    features), each with its fitted contribution, band, and reliability. forecast = baseline
    (persistence) + Σ fired-driver contributions, so the structure IS the explanation. With
    verified=true the active-driver set is run through the verified kernel — each driver is stamped
    proof_checked and a why_certification block is attached. Magnitudes/bands are statistical (outside
    the proof). Feature-flagged (AMBERTRACE_SYMBOLIC_FORECAST); 404 when disabled. PRECONDITION to serve
    a platform: a prediction config exists on the platform whose target_field is present and numeric in
    at least one ready/ingested dataset. No training and no minimum row count is required — when too few
    rows or too weak a signal yield no driver-rules, the response is an HONEST forecast: with the
    default baseline_mode=neural the value is the GBT prediction through the S2 confidence gate
    (forecast_tier=neural_scored when confident, neural_weak when below threshold, with
    neural_confidence_tau emitted separately — the raw GBT prediction is always served, never replaced;
    no_forecast only when no model exists); with other anchors it is the baseline anchor
    (forecast_tier=baseline_anchor; point_is_persistence==true ONLY when baseline_mode is persistence).
    WITH a real RMSE-based interval, not an error. Unmet preconditions return a STRUCTURED error (409
    when the target is absent from every dataset; 422 when the latest row's target is non-numeric),
    never a raw 404.

    ASYNC: returns 202 immediately with {job_id, poll, status:\"forecasting\"}; the fit runs in the
    background (minutes on wide panels). Poll GET /api/v1/jobs/{job_id} — on completion the job `result`
    IS the forecast payload described above; on failure the job status is failed, `error_message`
    carries the reason and `result.error` the structured {code, message, http_status} (the status the
    former synchronous endpoint returned, e.g. 409 target absent, 422 validation). An identical request
    already in flight returns the existing job_id (deduplicated=true). The 404 (flag off), 403 and
    config-not-found errors are still returned synchronously. Requires a user or session credential
    (platform-scoped keys get 403), since the job is polled via GET /jobs/{id}.

    Capability gating: requires the \"predictions\" capability (see GET /api/v1/capabilities). Returns
    403 capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (SymbolicForecastRequest): Request body for the symbolic-forecast "why" endpoint.

            Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction
            config's dataset: it induces human-readable driver-rules over the dataset's
            REAL features and composes the forecast as ``baseline + Σ fired drivers``, so
            the response carries an actionable *why* (the ordered drivers + their fitted
            contributions + reliability), not just a number. With ``verified=true`` the
            active-driver set is run through the verified kernel and each driver is
            stamped ``proof_checked``.

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
    body: SymbolicForecastRequest,
) -> Response[list[ValidationErrorModel]]:
    r"""Symbolic forecast with a proof-carrying WHY

     Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction config's dataset and
    returns the forecast WITH its WHY: the ordered driver-rules that fired (over the dataset's real
    features), each with its fitted contribution, band, and reliability. forecast = baseline
    (persistence) + Σ fired-driver contributions, so the structure IS the explanation. With
    verified=true the active-driver set is run through the verified kernel — each driver is stamped
    proof_checked and a why_certification block is attached. Magnitudes/bands are statistical (outside
    the proof). Feature-flagged (AMBERTRACE_SYMBOLIC_FORECAST); 404 when disabled. PRECONDITION to serve
    a platform: a prediction config exists on the platform whose target_field is present and numeric in
    at least one ready/ingested dataset. No training and no minimum row count is required — when too few
    rows or too weak a signal yield no driver-rules, the response is an HONEST forecast: with the
    default baseline_mode=neural the value is the GBT prediction through the S2 confidence gate
    (forecast_tier=neural_scored when confident, neural_weak when below threshold, with
    neural_confidence_tau emitted separately — the raw GBT prediction is always served, never replaced;
    no_forecast only when no model exists); with other anchors it is the baseline anchor
    (forecast_tier=baseline_anchor; point_is_persistence==true ONLY when baseline_mode is persistence).
    WITH a real RMSE-based interval, not an error. Unmet preconditions return a STRUCTURED error (409
    when the target is absent from every dataset; 422 when the latest row's target is non-numeric),
    never a raw 404.

    ASYNC: returns 202 immediately with {job_id, poll, status:\"forecasting\"}; the fit runs in the
    background (minutes on wide panels). Poll GET /api/v1/jobs/{job_id} — on completion the job `result`
    IS the forecast payload described above; on failure the job status is failed, `error_message`
    carries the reason and `result.error` the structured {code, message, http_status} (the status the
    former synchronous endpoint returned, e.g. 409 target absent, 422 validation). An identical request
    already in flight returns the existing job_id (deduplicated=true). The 404 (flag off), 403 and
    config-not-found errors are still returned synchronously. Requires a user or session credential
    (platform-scoped keys get 403), since the job is polled via GET /jobs/{id}.

    Capability gating: requires the \"predictions\" capability (see GET /api/v1/capabilities). Returns
    403 capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (SymbolicForecastRequest): Request body for the symbolic-forecast "why" endpoint.

            Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction
            config's dataset: it induces human-readable driver-rules over the dataset's
            REAL features and composes the forecast as ``baseline + Σ fired drivers``, so
            the response carries an actionable *why* (the ordered drivers + their fitted
            contributions + reliability), not just a number. With ``verified=true`` the
            active-driver set is run through the verified kernel and each driver is
            stamped ``proof_checked``.

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
    body: SymbolicForecastRequest,
) -> list[ValidationErrorModel] | None:
    r"""Symbolic forecast with a proof-carrying WHY

     Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction config's dataset and
    returns the forecast WITH its WHY: the ordered driver-rules that fired (over the dataset's real
    features), each with its fitted contribution, band, and reliability. forecast = baseline
    (persistence) + Σ fired-driver contributions, so the structure IS the explanation. With
    verified=true the active-driver set is run through the verified kernel — each driver is stamped
    proof_checked and a why_certification block is attached. Magnitudes/bands are statistical (outside
    the proof). Feature-flagged (AMBERTRACE_SYMBOLIC_FORECAST); 404 when disabled. PRECONDITION to serve
    a platform: a prediction config exists on the platform whose target_field is present and numeric in
    at least one ready/ingested dataset. No training and no minimum row count is required — when too few
    rows or too weak a signal yield no driver-rules, the response is an HONEST forecast: with the
    default baseline_mode=neural the value is the GBT prediction through the S2 confidence gate
    (forecast_tier=neural_scored when confident, neural_weak when below threshold, with
    neural_confidence_tau emitted separately — the raw GBT prediction is always served, never replaced;
    no_forecast only when no model exists); with other anchors it is the baseline anchor
    (forecast_tier=baseline_anchor; point_is_persistence==true ONLY when baseline_mode is persistence).
    WITH a real RMSE-based interval, not an error. Unmet preconditions return a STRUCTURED error (409
    when the target is absent from every dataset; 422 when the latest row's target is non-numeric),
    never a raw 404.

    ASYNC: returns 202 immediately with {job_id, poll, status:\"forecasting\"}; the fit runs in the
    background (minutes on wide panels). Poll GET /api/v1/jobs/{job_id} — on completion the job `result`
    IS the forecast payload described above; on failure the job status is failed, `error_message`
    carries the reason and `result.error` the structured {code, message, http_status} (the status the
    former synchronous endpoint returned, e.g. 409 target absent, 422 validation). An identical request
    already in flight returns the existing job_id (deduplicated=true). The 404 (flag off), 403 and
    config-not-found errors are still returned synchronously. Requires a user or session credential
    (platform-scoped keys get 403), since the job is polled via GET /jobs/{id}.

    Capability gating: requires the \"predictions\" capability (see GET /api/v1/capabilities). Returns
    403 capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (SymbolicForecastRequest): Request body for the symbolic-forecast "why" endpoint.

            Runs a STANDALONE, fully-transparent symbolic forecaster over the prediction
            config's dataset: it induces human-readable driver-rules over the dataset's
            REAL features and composes the forecast as ``baseline + Σ fired drivers``, so
            the response carries an actionable *why* (the ordered drivers + their fitted
            contributions + reliability), not just a number. With ``verified=true`` the
            active-driver set is run through the verified kernel and each driver is
            stamped ``proof_checked``.

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
