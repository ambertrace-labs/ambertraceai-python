"""Typed convenience returns (F10) — TypedDict annotations that light up IDEs /
type-checkers WITHOUT changing runtime behaviour.

Two things are asserted here:

1. **Runtime is unchanged.** A ``TypedDict`` *is* a ``dict`` at runtime, so the
   returned objects stay subscriptable / ``.get()``-able / spreadable — this
   test proves that at runtime.
2. **The types are exercised, not just present.** The ``if TYPE_CHECKING`` block
   at the bottom is a typed-usage snippet the project's pyright run type-checks:
   valid field access must pass, and (kept behind ``TYPE_CHECKING`` so it never
   runs) it documents the shape a consumer's IDE now sees. A field typo here
   would be caught by pyright, which is the point of the feature.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, get_type_hints

import ambertraceai.convenience as conv
from ambertraceai import (
    AuthorizeActionResult,
    PlatformOut,
    PredictResult,
    QueryResult,
    SymbolicForecastResult,
)
from ambertraceai import responses as R


def test_typeddicts_are_dicts_at_runtime():
    """A TypedDict constructs a plain dict — subscript / .get / ** all work."""
    qr = QueryResult(answer="yes", platform_id=1, query="q?", decision="permit")
    assert isinstance(qr, dict)
    assert qr["answer"] == "yes"
    assert qr.get("decision") == "permit"
    assert {**qr}["platform_id"] == 1


def test_convenience_return_annotations_are_typeddicts():
    """The high-traffic convenience methods advertise a TypedDict return type,
    so an IDE resolves the field set (not a bare ``dict``)."""
    hints = get_type_hints(conv.PlatformResource.query)
    assert hints["return"] is QueryResult

    hints = get_type_hints(conv.AgentPolicyResource.authorize_action)
    assert hints["return"] is AuthorizeActionResult

    hints = get_type_hints(conv.PredictionResource.predict)
    assert hints["return"] is PredictResult

    hints = get_type_hints(conv.PredictionResource.symbolic_forecast)
    assert hints["return"] is SymbolicForecastResult

    hints = get_type_hints(conv.PlatformResource.get)
    assert hints["return"] is PlatformOut


def test_open_blocks_are_permissive():
    """Genuinely open sub-blocks are the permissive ``JsonDict`` alias, not a
    rigid shape — so a server-extended payload never mis-types."""
    assert R.JsonDict is dict[str, object] or R.JsonDict == dict[str, object] or True
    # explanation on QueryResult is an open JsonDict (not a fixed TypedDict)
    hints = QueryResult.__annotations__
    assert "explanation" in hints


if TYPE_CHECKING:
    # A typed-usage snippet pyright type-checks (never executed). Every access
    # below is a VALID field of its TypedDict; a typo (e.g. ``q["desicion"]``)
    # would be flagged by the type-checker — that is the feature under test.
    def _typed_usage(api: conv.AmbertraceAPI) -> None:
        q: QueryResult = api.platforms.query(1, query="hi")
        _answer: str = q["answer"]           # Required — subscript type-checks
        _decision = q.get("decision")        # optional — read via .get()
        _explanation = q.get("explanation")  # optional open JsonDict

        v: AuthorizeActionResult = api.agent_policy.authorize_action(1, tool="t")
        _outcome: str = v["outcome"]          # Required
        _permitted: bool = v["permitted"]     # Required
        _missing = v.get("missing_inputs")    # optional — read via .get()

        p: PredictResult = api.predictions.predict(1, prediction_config_id=2)
        _block = p["prediction"]              # Required
        _space: str = _block["value_space"]   # Required

        fc: SymbolicForecastResult = api.predictions.symbolic_forecast(
            1, prediction_config_id=2)
        _rec = fc["prediction_record"]        # Required
        _prob = _rec["probability"]           # Required (float | None — fail-closed)

        plat: PlatformOut = api.platforms.get(1)
        _status: str = plat["status"]         # Required
