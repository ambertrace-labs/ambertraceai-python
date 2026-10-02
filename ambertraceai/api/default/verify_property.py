from http import HTTPStatus
from typing import Any
from urllib.parse import quote

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.validation_error_model import ValidationErrorModel
from ...models.verify_property_request import VerifyPropertyRequest
from ...models.verify_property_response import VerifyPropertyResponse
from ...types import Response


def _get_kwargs(
    id: int,
    *,
    body: VerifyPropertyRequest,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/api/v1/platforms/{id}/verify-property".format(
            id=quote(str(id), safe=""),
        ),
    }

    _kwargs["json"] = body.to_dict()

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: AuthenticatedClient | Client, response: httpx.Response
) -> VerifyPropertyResponse | list[ValidationErrorModel] | None:
    if response.status_code == 200:
        response_200 = VerifyPropertyResponse.from_dict(response.json())

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
) -> Response[VerifyPropertyResponse | list[ValidationErrorModel]]:
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
    body: VerifyPropertyRequest,
) -> Response[VerifyPropertyResponse | list[ValidationErrorModel]]:
    r"""Certify a universal property over a finite space (certified search)

     Certified search: decides a UNIVERSAL claim (\"for every profile and every deviation ...\") over a
    finite, rule-defined space and returns EITHER a machine-checked exhaustiveness verdict
    (result=HOLDS, certified=\"exhaustive\", search.complete=true, search.space_size = the product of
    the declared domain sizes) OR a certified counterexample (result=VIOLATED, certified=\"witness\", a
    `witness` member that is independently re-certified through the trusted kernel) OR an explicit
    result=ABSTAIN (space above your `bound` or the platform ceiling, time budget exceeded, unsupported
    request) -- never a silent partial pass. result, certified, proof_checked, proof_summary and search
    are computed from ONE source, the proven searchcheck binary's decision.

    Property library (v1): `strategy_proof` (no agent can profit from misreporting) over the mechanism
    library plurality / majority / vickrey / first_price, declared in `space` (see VerifyPropertySpace).
    The platform scopes access, audit and config (`lean_checker_mode`, a lowered
    `certified_search_max_space`); the mechanism is declared in the request.

    Capability gating: requires the \"query\" capability (see GET /api/v1/capabilities). Returns 403
    capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (VerifyPropertyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VerifyPropertyResponse | list[ValidationErrorModel]]
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
    body: VerifyPropertyRequest,
) -> VerifyPropertyResponse | list[ValidationErrorModel] | None:
    r"""Certify a universal property over a finite space (certified search)

     Certified search: decides a UNIVERSAL claim (\"for every profile and every deviation ...\") over a
    finite, rule-defined space and returns EITHER a machine-checked exhaustiveness verdict
    (result=HOLDS, certified=\"exhaustive\", search.complete=true, search.space_size = the product of
    the declared domain sizes) OR a certified counterexample (result=VIOLATED, certified=\"witness\", a
    `witness` member that is independently re-certified through the trusted kernel) OR an explicit
    result=ABSTAIN (space above your `bound` or the platform ceiling, time budget exceeded, unsupported
    request) -- never a silent partial pass. result, certified, proof_checked, proof_summary and search
    are computed from ONE source, the proven searchcheck binary's decision.

    Property library (v1): `strategy_proof` (no agent can profit from misreporting) over the mechanism
    library plurality / majority / vickrey / first_price, declared in `space` (see VerifyPropertySpace).
    The platform scopes access, audit and config (`lean_checker_mode`, a lowered
    `certified_search_max_space`); the mechanism is declared in the request.

    Capability gating: requires the \"query\" capability (see GET /api/v1/capabilities). Returns 403
    capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (VerifyPropertyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VerifyPropertyResponse | list[ValidationErrorModel]
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
    body: VerifyPropertyRequest,
) -> Response[VerifyPropertyResponse | list[ValidationErrorModel]]:
    r"""Certify a universal property over a finite space (certified search)

     Certified search: decides a UNIVERSAL claim (\"for every profile and every deviation ...\") over a
    finite, rule-defined space and returns EITHER a machine-checked exhaustiveness verdict
    (result=HOLDS, certified=\"exhaustive\", search.complete=true, search.space_size = the product of
    the declared domain sizes) OR a certified counterexample (result=VIOLATED, certified=\"witness\", a
    `witness` member that is independently re-certified through the trusted kernel) OR an explicit
    result=ABSTAIN (space above your `bound` or the platform ceiling, time budget exceeded, unsupported
    request) -- never a silent partial pass. result, certified, proof_checked, proof_summary and search
    are computed from ONE source, the proven searchcheck binary's decision.

    Property library (v1): `strategy_proof` (no agent can profit from misreporting) over the mechanism
    library plurality / majority / vickrey / first_price, declared in `space` (see VerifyPropertySpace).
    The platform scopes access, audit and config (`lean_checker_mode`, a lowered
    `certified_search_max_space`); the mechanism is declared in the request.

    Capability gating: requires the \"query\" capability (see GET /api/v1/capabilities). Returns 403
    capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (VerifyPropertyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[VerifyPropertyResponse | list[ValidationErrorModel]]
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
    body: VerifyPropertyRequest,
) -> VerifyPropertyResponse | list[ValidationErrorModel] | None:
    r"""Certify a universal property over a finite space (certified search)

     Certified search: decides a UNIVERSAL claim (\"for every profile and every deviation ...\") over a
    finite, rule-defined space and returns EITHER a machine-checked exhaustiveness verdict
    (result=HOLDS, certified=\"exhaustive\", search.complete=true, search.space_size = the product of
    the declared domain sizes) OR a certified counterexample (result=VIOLATED, certified=\"witness\", a
    `witness` member that is independently re-certified through the trusted kernel) OR an explicit
    result=ABSTAIN (space above your `bound` or the platform ceiling, time budget exceeded, unsupported
    request) -- never a silent partial pass. result, certified, proof_checked, proof_summary and search
    are computed from ONE source, the proven searchcheck binary's decision.

    Property library (v1): `strategy_proof` (no agent can profit from misreporting) over the mechanism
    library plurality / majority / vickrey / first_price, declared in `space` (see VerifyPropertySpace).
    The platform scopes access, audit and config (`lean_checker_mode`, a lowered
    `certified_search_max_space`); the mechanism is declared in the request.

    Capability gating: requires the \"query\" capability (see GET /api/v1/capabilities). Returns 403
    capability_disabled when the capability is not enabled for the org.

    Args:
        id (int): Resource ID
        body (VerifyPropertyRequest):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        VerifyPropertyResponse | list[ValidationErrorModel]
    """

    return (
        await asyncio_detailed(
            id=id,
            client=client,
            body=body,
        )
    ).parsed
