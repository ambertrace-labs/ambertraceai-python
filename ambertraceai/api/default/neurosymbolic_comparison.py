from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.neurosymbolic_comparison_query import NeurosymbolicComparisonQuery
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: NeurosymbolicComparisonQuery,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/neurosymbolic-comparison".format(
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
    body: NeurosymbolicComparisonQuery,
) -> Response[list[ValidationErrorModel]]:
    r"""Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, n_pending_rules, fire_rate, mode}. Set include_pending=true
    to ALSO apply the accepted-but-pending discovered rules read-only (a \"what-if\" preview before the
    approval gate; mode=preview_pending). Set include_series=true to ALSO get a per-period \"series\"
    array over the SAME holdout (each entry {index, time, actual, neural, neurosymbolic, rule_fired}) so
    the head-to-head can be charted over time; it reconciles with the aggregate metrics and is omitted
    by default. Timeseries configs only. feature_overrides applies a what-if override to the FORWARD
    projection only. The backtest-scoring path (expanding-window holdout scored against real historical
    actuals) is NEVER overridden — the head-to-head metrics are always the real historical skill. The
    forward what-if number and the backtest impact information are returned side-by-side so the user
    sees both \"what-if projection under overrides\" and \"how this model performed historically\".

    Args:
        id (int): Resource ID
        body (NeurosymbolicComparisonQuery): Request body for the neural-vs-neurosymbolic
            comparison.

            The comparison scores BOTH branches against KNOWN historical actuals over
            the expanding-window holdout (the backtest is NEVER overridden).  When
            ``feature_overrides`` is supplied, a FORWARD what-if projection is
            computed alongside the backtest: the overrides are injected into the latest
            data row and propagated through the neural+symbolic forward forecast.  The
            response carries both the forward what-if result and the backtest impact
            information side-by-side (``forward_whatif`` + ``backtest_impact``).

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
    body: NeurosymbolicComparisonQuery,
) -> list[ValidationErrorModel] | None:
    r"""Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, n_pending_rules, fire_rate, mode}. Set include_pending=true
    to ALSO apply the accepted-but-pending discovered rules read-only (a \"what-if\" preview before the
    approval gate; mode=preview_pending). Set include_series=true to ALSO get a per-period \"series\"
    array over the SAME holdout (each entry {index, time, actual, neural, neurosymbolic, rule_fired}) so
    the head-to-head can be charted over time; it reconciles with the aggregate metrics and is omitted
    by default. Timeseries configs only. feature_overrides applies a what-if override to the FORWARD
    projection only. The backtest-scoring path (expanding-window holdout scored against real historical
    actuals) is NEVER overridden — the head-to-head metrics are always the real historical skill. The
    forward what-if number and the backtest impact information are returned side-by-side so the user
    sees both \"what-if projection under overrides\" and \"how this model performed historically\".

    Args:
        id (int): Resource ID
        body (NeurosymbolicComparisonQuery): Request body for the neural-vs-neurosymbolic
            comparison.

            The comparison scores BOTH branches against KNOWN historical actuals over
            the expanding-window holdout (the backtest is NEVER overridden).  When
            ``feature_overrides`` is supplied, a FORWARD what-if projection is
            computed alongside the backtest: the overrides are injected into the latest
            data row and propagated through the neural+symbolic forward forecast.  The
            response carries both the forward what-if result and the backtest impact
            information side-by-side (``forward_whatif`` + ``backtest_impact``).

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
    body: NeurosymbolicComparisonQuery,
) -> Response[list[ValidationErrorModel]]:
    r"""Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, n_pending_rules, fire_rate, mode}. Set include_pending=true
    to ALSO apply the accepted-but-pending discovered rules read-only (a \"what-if\" preview before the
    approval gate; mode=preview_pending). Set include_series=true to ALSO get a per-period \"series\"
    array over the SAME holdout (each entry {index, time, actual, neural, neurosymbolic, rule_fired}) so
    the head-to-head can be charted over time; it reconciles with the aggregate metrics and is omitted
    by default. Timeseries configs only. feature_overrides applies a what-if override to the FORWARD
    projection only. The backtest-scoring path (expanding-window holdout scored against real historical
    actuals) is NEVER overridden — the head-to-head metrics are always the real historical skill. The
    forward what-if number and the backtest impact information are returned side-by-side so the user
    sees both \"what-if projection under overrides\" and \"how this model performed historically\".

    Args:
        id (int): Resource ID
        body (NeurosymbolicComparisonQuery): Request body for the neural-vs-neurosymbolic
            comparison.

            The comparison scores BOTH branches against KNOWN historical actuals over
            the expanding-window holdout (the backtest is NEVER overridden).  When
            ``feature_overrides`` is supplied, a FORWARD what-if projection is
            computed alongside the backtest: the overrides are injected into the latest
            data row and propagated through the neural+symbolic forward forecast.  The
            response carries both the forward what-if result and the backtest impact
            information side-by-side (``forward_whatif`` + ``backtest_impact``).

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
    body: NeurosymbolicComparisonQuery,
) -> list[ValidationErrorModel] | None:
    r"""Neural-vs-neurosymbolic backtest comparison

     Starts an async comparison that scores the trained model TWO ways over the same expanding-window
    holdout: neural (model alone) and neurosymbolic (after the platform's active adjustment+constraint
    rules are applied exactly as the live predict path applies them). Returns 202 with a job_id — poll
    GET /api/v1/jobs/{job_id}; the completed job result carries {neural, neurosymbolic, delta,
    n_adjustment_rules, n_constraint_rules, n_pending_rules, fire_rate, mode}. Set include_pending=true
    to ALSO apply the accepted-but-pending discovered rules read-only (a \"what-if\" preview before the
    approval gate; mode=preview_pending). Set include_series=true to ALSO get a per-period \"series\"
    array over the SAME holdout (each entry {index, time, actual, neural, neurosymbolic, rule_fired}) so
    the head-to-head can be charted over time; it reconciles with the aggregate metrics and is omitted
    by default. Timeseries configs only. feature_overrides applies a what-if override to the FORWARD
    projection only. The backtest-scoring path (expanding-window holdout scored against real historical
    actuals) is NEVER overridden — the head-to-head metrics are always the real historical skill. The
    forward what-if number and the backtest impact information are returned side-by-side so the user
    sees both \"what-if projection under overrides\" and \"how this model performed historically\".

    Args:
        id (int): Resource ID
        body (NeurosymbolicComparisonQuery): Request body for the neural-vs-neurosymbolic
            comparison.

            The comparison scores BOTH branches against KNOWN historical actuals over
            the expanding-window holdout (the backtest is NEVER overridden).  When
            ``feature_overrides`` is supplied, a FORWARD what-if projection is
            computed alongside the backtest: the overrides are injected into the latest
            data row and propagated through the neural+symbolic forward forecast.  The
            response carries both the forward what-if result and the backtest impact
            information side-by-side (``forward_whatif`` + ``backtest_impact``).

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
