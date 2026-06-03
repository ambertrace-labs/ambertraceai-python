from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.query_request import QueryRequest
from ...models.query_response import QueryResponse
from ...models.validation_error_model import ValidationErrorModel
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: QueryRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/query".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> QueryResponse | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = QueryResponse.from_dict(response.json())

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
) -> Response[QueryResponse | list[ValidationErrorModel]]:
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
    body: QueryRequest,
) -> Response[QueryResponse | list[ValidationErrorModel]]:
    """Run neurosymbolic query

     Executes the full neurosymbolic pipeline: neural retrieval from the knowledge graph, symbolic rule
    evaluation (ontology constraints auto-fire), graph context enrichment, LLM answer generation, and
    explainability trace. Ontology constraints (compiled at build time) and any approved suggested rules
    all fire automatically. Requires an active platform (status 'active').

    Verified-profile platforms additionally: gate input facts by the confidence threshold τ (rejected
    facts appear in explanation.rejected_facts), evaluate rules with a fail-closed Prolog engine, and
    independently re-derive the decision against the trusted kernel. The response then carries
    proof_checked=true and a proof_summary (full derivation in explanation.proof). If a verified
    decision cannot be certified — engine/kernel disagreement, a non-stratifiable or manifest-violating
    active rule set, or the engine being unavailable — the query fails closed with HTTP 503 and returns
    no answer. For non-verified platforms proof_checked is null.

    Args:
        id (int): Resource ID
        body (QueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[QueryResponse | list[ValidationErrorModel]]
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
    body: QueryRequest,
) -> QueryResponse | list[ValidationErrorModel] | None:
    """Run neurosymbolic query

     Executes the full neurosymbolic pipeline: neural retrieval from the knowledge graph, symbolic rule
    evaluation (ontology constraints auto-fire), graph context enrichment, LLM answer generation, and
    explainability trace. Ontology constraints (compiled at build time) and any approved suggested rules
    all fire automatically. Requires an active platform (status 'active').

    Verified-profile platforms additionally: gate input facts by the confidence threshold τ (rejected
    facts appear in explanation.rejected_facts), evaluate rules with a fail-closed Prolog engine, and
    independently re-derive the decision against the trusted kernel. The response then carries
    proof_checked=true and a proof_summary (full derivation in explanation.proof). If a verified
    decision cannot be certified — engine/kernel disagreement, a non-stratifiable or manifest-violating
    active rule set, or the engine being unavailable — the query fails closed with HTTP 503 and returns
    no answer. For non-verified platforms proof_checked is null.

    Args:
        id (int): Resource ID
        body (QueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        QueryResponse | list[ValidationErrorModel]
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
    body: QueryRequest,
) -> Response[QueryResponse | list[ValidationErrorModel]]:
    """Run neurosymbolic query

     Executes the full neurosymbolic pipeline: neural retrieval from the knowledge graph, symbolic rule
    evaluation (ontology constraints auto-fire), graph context enrichment, LLM answer generation, and
    explainability trace. Ontology constraints (compiled at build time) and any approved suggested rules
    all fire automatically. Requires an active platform (status 'active').

    Verified-profile platforms additionally: gate input facts by the confidence threshold τ (rejected
    facts appear in explanation.rejected_facts), evaluate rules with a fail-closed Prolog engine, and
    independently re-derive the decision against the trusted kernel. The response then carries
    proof_checked=true and a proof_summary (full derivation in explanation.proof). If a verified
    decision cannot be certified — engine/kernel disagreement, a non-stratifiable or manifest-violating
    active rule set, or the engine being unavailable — the query fails closed with HTTP 503 and returns
    no answer. For non-verified platforms proof_checked is null.

    Args:
        id (int): Resource ID
        body (QueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[QueryResponse | list[ValidationErrorModel]]
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
    body: QueryRequest,
) -> QueryResponse | list[ValidationErrorModel] | None:
    """Run neurosymbolic query

     Executes the full neurosymbolic pipeline: neural retrieval from the knowledge graph, symbolic rule
    evaluation (ontology constraints auto-fire), graph context enrichment, LLM answer generation, and
    explainability trace. Ontology constraints (compiled at build time) and any approved suggested rules
    all fire automatically. Requires an active platform (status 'active').

    Verified-profile platforms additionally: gate input facts by the confidence threshold τ (rejected
    facts appear in explanation.rejected_facts), evaluate rules with a fail-closed Prolog engine, and
    independently re-derive the decision against the trusted kernel. The response then carries
    proof_checked=true and a proof_summary (full derivation in explanation.proof). If a verified
    decision cannot be certified — engine/kernel disagreement, a non-stratifiable or manifest-violating
    active rule set, or the engine being unavailable — the query fails closed with HTTP 503 and returns
    no answer. For non-verified platforms proof_checked is null.

    Args:
        id (int): Resource ID
        body (QueryRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        QueryResponse | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
