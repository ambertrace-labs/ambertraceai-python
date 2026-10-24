from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.step_request import StepRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    sid: str,
    *,
    body: StepRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/agent-sessions/{sid}/step".format(
            sid=quote(str(sid), safe=""),
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
    sid: str,
    *,
    client: AuthenticatedClient | Client,
    body: StepRequest,
) -> Response[list[ValidationErrorModel]]:
    """Run one mediated agent step (propose → gate → execute-or-block)

     The agent proposes a tool call (explicitly via `action`+`context`, or by letting the sample agent
    decide). The harness gates it through the verified policy; on a certified permit it executes the
    effect (mock echo) and records it; otherwise it blocks and records — with proof either way. The
    harness is the sole executor: no effect occurs without a prior certified permit.

    The recorded `step.verdict` carries the same `status` and `outcome` as /authorize-action — `status`
    `decided` | `indeterminate` | `unavailable`, `outcome` `permit` | `deny` | null — plus
    `missing_inputs` / `stalled_stage` / `query_diagnostics` on an `indeterminate` status. A step
    executes ONLY on a certified permit (`permitted` AND `proof_checked`); `indeterminate` /
    `unavailable` are fail-closed non-permits that never execute (`executed=false`). Feature-flagged.

    Args:
        sid (str): Agent session id
        body (StepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        sid=sid,
        body=body,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    sid: str,
    *,
    client: AuthenticatedClient | Client,
    body: StepRequest,
) -> list[ValidationErrorModel] | None:
    """Run one mediated agent step (propose → gate → execute-or-block)

     The agent proposes a tool call (explicitly via `action`+`context`, or by letting the sample agent
    decide). The harness gates it through the verified policy; on a certified permit it executes the
    effect (mock echo) and records it; otherwise it blocks and records — with proof either way. The
    harness is the sole executor: no effect occurs without a prior certified permit.

    The recorded `step.verdict` carries the same `status` and `outcome` as /authorize-action — `status`
    `decided` | `indeterminate` | `unavailable`, `outcome` `permit` | `deny` | null — plus
    `missing_inputs` / `stalled_stage` / `query_diagnostics` on an `indeterminate` status. A step
    executes ONLY on a certified permit (`permitted` AND `proof_checked`); `indeterminate` /
    `unavailable` are fail-closed non-permits that never execute (`executed=false`). Feature-flagged.

    Args:
        sid (str): Agent session id
        body (StepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return sync_detailed(
        sid=sid,
        client=client,
        body=body,
    ).parsed


async def asyncio_detailed(
    sid: str,
    *,
    client: AuthenticatedClient | Client,
    body: StepRequest,
) -> Response[list[ValidationErrorModel]]:
    """Run one mediated agent step (propose → gate → execute-or-block)

     The agent proposes a tool call (explicitly via `action`+`context`, or by letting the sample agent
    decide). The harness gates it through the verified policy; on a certified permit it executes the
    effect (mock echo) and records it; otherwise it blocks and records — with proof either way. The
    harness is the sole executor: no effect occurs without a prior certified permit.

    The recorded `step.verdict` carries the same `status` and `outcome` as /authorize-action — `status`
    `decided` | `indeterminate` | `unavailable`, `outcome` `permit` | `deny` | null — plus
    `missing_inputs` / `stalled_stage` / `query_diagnostics` on an `indeterminate` status. A step
    executes ONLY on a certified permit (`permitted` AND `proof_checked`); `indeterminate` /
    `unavailable` are fail-closed non-permits that never execute (`executed=false`). Feature-flagged.

    Args:
        sid (str): Agent session id
        body (StepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[list[ValidationErrorModel]]
    """

    kwargs = _get_kwargs(
        sid=sid,
        body=body,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    sid: str,
    *,
    client: AuthenticatedClient | Client,
    body: StepRequest,
) -> list[ValidationErrorModel] | None:
    """Run one mediated agent step (propose → gate → execute-or-block)

     The agent proposes a tool call (explicitly via `action`+`context`, or by letting the sample agent
    decide). The harness gates it through the verified policy; on a certified permit it executes the
    effect (mock echo) and records it; otherwise it blocks and records — with proof either way. The
    harness is the sole executor: no effect occurs without a prior certified permit.

    The recorded `step.verdict` carries the same `status` and `outcome` as /authorize-action — `status`
    `decided` | `indeterminate` | `unavailable`, `outcome` `permit` | `deny` | null — plus
    `missing_inputs` / `stalled_stage` / `query_diagnostics` on an `indeterminate` status. A step
    executes ONLY on a certified permit (`permitted` AND `proof_checked`); `indeterminate` /
    `unavailable` are fail-closed non-permits that never execute (`executed=false`). Feature-flagged.

    Args:
        sid (str): Agent session id
        body (StepRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            sid=sid,
            client=client,
            body=body,
        )
    ).parsed
