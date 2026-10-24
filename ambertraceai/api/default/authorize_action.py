from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.authorize_action_request import AuthorizeActionRequest
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: AuthorizeActionRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/authorize-action".format(
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
    body: AuthorizeActionRequest,
) -> Response[list[ValidationErrorModel]]:
    r"""Authorize an agent tool-call against the verified policy

     Proof-carrying gate. Maps the action's args + context to the certified facts the policy reasons
    over, returning a certified permit/deny verdict with its machine-checked proof. Fail-closed: a
    rejected fact, proof-check failure, or unavailable engine yields no permit.

    The verdict carries a `status` — `decided` (a decision-table row decided), `indeterminate` (a
    REQUIRED input was missing/underivable — fail-closed, NOT a denial; the remedy is to supply the
    named field) or `unavailable` (the verified reasoning engine is temporarily down) — and an `outcome`
    narrowed to `permit` | `deny` | null: `permit` iff the deciding row `permits`, null when nothing was
    decided. `decision` is the deciding row's label and `permitted` is `outcome == \"permit\"`. For
    `indeterminate` the verdict also carries `missing_inputs` (the declared field name(s) the chain
    needed but were neither supplied nor derived), `stalled_stage`, and a `query_diagnostics` block
    (identical shape to the query route: `missing_atoms`, `deciding_rule`, `rejected_facts`,
    `stalled_stage`). INVARIANT: for `indeterminate` and `unavailable` the `permitted` flag stays false
    and `proof_checked` stays false — `status`/`missing_inputs` are DESCRIPTIVE ONLY and never authorize
    execution.

    Feature-flagged (AMBERTRACE_AGENT_POLICY_GATE); 404 when disabled.

    Args:
        id (int): Resource ID
        body (AuthorizeActionRequest):

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
    body: AuthorizeActionRequest,
) -> list[ValidationErrorModel] | None:
    r"""Authorize an agent tool-call against the verified policy

     Proof-carrying gate. Maps the action's args + context to the certified facts the policy reasons
    over, returning a certified permit/deny verdict with its machine-checked proof. Fail-closed: a
    rejected fact, proof-check failure, or unavailable engine yields no permit.

    The verdict carries a `status` — `decided` (a decision-table row decided), `indeterminate` (a
    REQUIRED input was missing/underivable — fail-closed, NOT a denial; the remedy is to supply the
    named field) or `unavailable` (the verified reasoning engine is temporarily down) — and an `outcome`
    narrowed to `permit` | `deny` | null: `permit` iff the deciding row `permits`, null when nothing was
    decided. `decision` is the deciding row's label and `permitted` is `outcome == \"permit\"`. For
    `indeterminate` the verdict also carries `missing_inputs` (the declared field name(s) the chain
    needed but were neither supplied nor derived), `stalled_stage`, and a `query_diagnostics` block
    (identical shape to the query route: `missing_atoms`, `deciding_rule`, `rejected_facts`,
    `stalled_stage`). INVARIANT: for `indeterminate` and `unavailable` the `permitted` flag stays false
    and `proof_checked` stays false — `status`/`missing_inputs` are DESCRIPTIVE ONLY and never authorize
    execution.

    Feature-flagged (AMBERTRACE_AGENT_POLICY_GATE); 404 when disabled.

    Args:
        id (int): Resource ID
        body (AuthorizeActionRequest):

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
    body: AuthorizeActionRequest,
) -> Response[list[ValidationErrorModel]]:
    r"""Authorize an agent tool-call against the verified policy

     Proof-carrying gate. Maps the action's args + context to the certified facts the policy reasons
    over, returning a certified permit/deny verdict with its machine-checked proof. Fail-closed: a
    rejected fact, proof-check failure, or unavailable engine yields no permit.

    The verdict carries a `status` — `decided` (a decision-table row decided), `indeterminate` (a
    REQUIRED input was missing/underivable — fail-closed, NOT a denial; the remedy is to supply the
    named field) or `unavailable` (the verified reasoning engine is temporarily down) — and an `outcome`
    narrowed to `permit` | `deny` | null: `permit` iff the deciding row `permits`, null when nothing was
    decided. `decision` is the deciding row's label and `permitted` is `outcome == \"permit\"`. For
    `indeterminate` the verdict also carries `missing_inputs` (the declared field name(s) the chain
    needed but were neither supplied nor derived), `stalled_stage`, and a `query_diagnostics` block
    (identical shape to the query route: `missing_atoms`, `deciding_rule`, `rejected_facts`,
    `stalled_stage`). INVARIANT: for `indeterminate` and `unavailable` the `permitted` flag stays false
    and `proof_checked` stays false — `status`/`missing_inputs` are DESCRIPTIVE ONLY and never authorize
    execution.

    Feature-flagged (AMBERTRACE_AGENT_POLICY_GATE); 404 when disabled.

    Args:
        id (int): Resource ID
        body (AuthorizeActionRequest):

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
    body: AuthorizeActionRequest,
) -> list[ValidationErrorModel] | None:
    r"""Authorize an agent tool-call against the verified policy

     Proof-carrying gate. Maps the action's args + context to the certified facts the policy reasons
    over, returning a certified permit/deny verdict with its machine-checked proof. Fail-closed: a
    rejected fact, proof-check failure, or unavailable engine yields no permit.

    The verdict carries a `status` — `decided` (a decision-table row decided), `indeterminate` (a
    REQUIRED input was missing/underivable — fail-closed, NOT a denial; the remedy is to supply the
    named field) or `unavailable` (the verified reasoning engine is temporarily down) — and an `outcome`
    narrowed to `permit` | `deny` | null: `permit` iff the deciding row `permits`, null when nothing was
    decided. `decision` is the deciding row's label and `permitted` is `outcome == \"permit\"`. For
    `indeterminate` the verdict also carries `missing_inputs` (the declared field name(s) the chain
    needed but were neither supplied nor derived), `stalled_stage`, and a `query_diagnostics` block
    (identical shape to the query route: `missing_atoms`, `deciding_rule`, `rejected_facts`,
    `stalled_stage`). INVARIANT: for `indeterminate` and `unavailable` the `permitted` flag stays false
    and `proof_checked` stays false — `status`/`missing_inputs` are DESCRIPTIVE ONLY and never authorize
    execution.

    Feature-flagged (AMBERTRACE_AGENT_POLICY_GATE); 404 when disabled.

    Args:
        id (int): Resource ID
        body (AuthorizeActionRequest):

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
