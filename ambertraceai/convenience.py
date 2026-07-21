# Copyright (c) 2026 Ambertrace Labs Ltd.
# All rights reserved.
#
# This source code is the proprietary and confidential property of
# Ambertrace Labs Ltd. No part of this file may be reproduced, stored,
# transmitted, or used in any form or by any means without the prior
# written permission of Ambertrace Labs Ltd. No license, express or
# implied, is granted herein.
#
# Contact: legal@ambertrace.ai

"""AmbertraceAI Python SDK — convenience layer over the generated client."""

from __future__ import annotations

import os
import random
import time
import urllib.parse
from typing import Any, Callable, cast

import httpx

# Return-shape TypedDicts (additive typing only — see ambertraceai/responses.py).
# With ``from __future__ import annotations`` every annotation is a string, so
# these names are used purely for IDE autocomplete / type-checking and add no
# runtime cost; each convenience method still returns a plain dict / AttrDict.
# NB: named ``responses`` (not ``types``) so it never shadows the generated
# client's own ``ambertraceai/types.py`` (Unset/Response/File) at overlay time.
from .responses import (
    AgentPolicyStatus,
    AuthorResult,
    AuthorizeActionResult,
    BuildQuality,
    BuildQualityCheck,
    DatasetOut,
    DiscoveredRules,
    DiscoverySummary,
    DomainOut,
    ForecastOut,
    JobOut,
    NeurosymbolicComparison,
    PlatformOut,
    PlatformStatusOut,
    PredictResult,
    PredictionConfigOut,
    ResidualDiagnosis,
    SessionResult,
    StepResult,
    SymbolicForecastResult,
    QueryResult,
)

# Sentinel for "no progress marker observed yet" so the first poll always counts
# as forward progress (distinct from any real status/progress tuple).
_UNSET = object()


class AttrDict(dict):
    """A ``dict`` that also exposes its keys as attributes.

    Returned by the convenience methods so a result is BOTH subscriptable
    (``result["id"]`` — the long-standing shape, unchanged) AND attribute-
    accessible (``result.id``) for IDE autocomplete / discoverability. Nested
    dicts are wrapped lazily on access, so ``result.platform.id`` works too.

    This is deliberately a plain ``dict`` subclass rather than a generated
    model class: every existing ``[...]`` access, ``.get(...)``, ``in`` test,
    ``json.dumps(...)`` and ``**spread`` keeps working byte-for-byte — the
    attribute access is purely additive and back-compatible.

    Note: a key whose name collides with a built-in ``dict`` method (``items``,
    ``keys``, ``values``, ``get``, ``update``, ...) resolves to the method on
    attribute access; read such a key via subscript (``d["items"]``).
    """

    def __getattr__(self, name: str) -> Any:
        try:
            value = self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc
        return _wrap(value)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        try:
            del self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc


def _wrap(value: Any) -> Any:
    """Recursively wrap dicts as :class:`AttrDict` (lists element-wise).

    Idempotent and cheap: scalars pass through untouched, an existing
    ``AttrDict`` is returned as-is.
    """
    if isinstance(value, AttrDict):
        return value
    if isinstance(value, dict):
        return AttrDict(value)
    if isinstance(value, list):
        return [_wrap(v) for v in value]
    return value


# The id of a created job/platform arrives under different keys across the
# API's create/dispatch envelopes (`id`, `platform_id`, nested `platform.id`,
# `job_id`, `build_job.job.id`, ...). The SDK absorbs this inconsistency so
# callers never hand-roll multi-shape unwrapping (see feature-sdk-dx item 4).
def _extract_id(body: Any) -> Any:
    """Best-effort stable resource id from a create/dispatch response.

    Tries the common top-level keys, then a nested ``platform``/``dataset``/
    ``domain`` object's ``id``. Returns ``None`` if nothing id-like is present
    (the caller can still read the raw shape).
    """
    if not isinstance(body, dict):
        return None
    for key in ("id", "platform_id", "dataset_id", "domain_id"):
        if body.get(key) is not None:
            return body[key]
    for nested in ("platform", "dataset", "domain"):
        obj = body.get(nested)
        if isinstance(obj, dict) and obj.get("id") is not None:
            return obj["id"]
    return None


def _extract_job_id(body: Any) -> Any:
    """Best-effort stable job id from a create/dispatch response.

    Handles ``job_id``, a nested ``job.id``, and ``build_job.job.id`` /
    ``build_job.id`` (platform create returns the build job under ``build_job``).
    Returns ``None`` when the response carries no job.
    """
    if not isinstance(body, dict):
        return None
    if body.get("job_id") is not None:
        return body["job_id"]
    for nested in ("job", "build_job"):
        obj = body.get(nested)
        if isinstance(obj, dict):
            if obj.get("job_id") is not None:
                return obj["job_id"]
            inner = obj.get("job")
            if isinstance(inner, dict) and inner.get("id") is not None:
                return inner["id"]
            if obj.get("id") is not None:
                return obj["id"]
    return None


def _normalise_envelope(body: Any) -> Any:
    """Wrap a response as :class:`AttrDict` and stamp stable ``id`` / ``job_id``.

    Back-compatible: never overwrites an id/job_id the body already carries at
    the top level; only *fills in* a normalised value derived from a nested or
    differently-keyed shape when the top-level key is absent. Non-dict bodies
    (lists, scalars) pass through ``_wrap`` unchanged.
    """
    if not isinstance(body, dict):
        return _wrap(body)
    wrapped = _wrap(body)
    if wrapped.get("id") is None:
        rid = _extract_id(body)
        if rid is not None:
            wrapped["id"] = rid
    if wrapped.get("job_id") is None:
        jid = _extract_job_id(body)
        if jid is not None:
            wrapped["job_id"] = jid
    return wrapped


def _coerce_details(details: Any) -> list[dict]:
    """Normalise an API ``error.details`` value to ``list[dict]``.

    The API returns a list of ``{"field", "message"}`` objects, but be robust:
    a missing/None/non-list value (or a list with non-dict entries) yields ``[]``
    so the SDK never raises while constructing an error.
    """
    if not isinstance(details, list):
        return []
    return [d for d in details if isinstance(d, dict)]


def _format_details(details: list[dict]) -> str:
    """Render details as ``field: message`` lines for inclusion in ``str(e)``."""
    parts = []
    for d in details:
        field = d.get("field")
        msg = d.get("message")
        if field and msg:
            parts.append(f"{field}: {msg}")
        elif msg:
            parts.append(str(msg))
        elif field:
            parts.append(str(field))
    return "; ".join(parts)


class AmbertraceError(Exception):
    """Error raised on a non-2xx API response.

    Backward-compatible attributes ``status_code`` and ``code`` are preserved.
    When the API returns a structured ``error.details`` list (e.g. the verified
    fail-closed 503 naming the rejected fact), it is exposed as ``details`` and
    folded into ``str(e)`` so a bare ``print(e)`` shows *which fact* was rejected.

    For a rule create/edit rejected by the data-driven-ontology column-mapping
    gate (``code == "schema_conflict"``, HTTP 400), the structured
    ``schema_reconciliation`` report — ``{status, augmented, conflicts}`` — is
    exposed as the :attr:`schema_reconciliation` attribute (and the
    :attr:`unmappable_fields` convenience), so a caller can show exactly which
    field references have no matching data column.

    For a verified ``platforms.query`` that fails closed (the engine could not
    certify a decision), the structured diagnostic fields the platform attaches
    to the error body — :attr:`missing_atoms`, :attr:`deciding_rule`,
    :attr:`rejected_facts` (also folded from ``details``) and
    :attr:`stalled_stage` — are surfaced so a caller can see *which* atom was
    missing without string-parsing the prose message (feature-sdk-dx item 3).
    These bring the query failure path to parity with
    ``agent_policy.authorize_action``, which already returns structured
    ``rejected_facts`` / ``deciding_rule``. Each is ``None``/``[]`` when the API
    did not supply it (back-compatible — older deployments simply omit them).
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
        schema_reconciliation: Any = None,
        *,
        missing_atoms: Any = None,
        deciding_rule: Any = None,
        rejected_facts: Any = None,
        stalled_stage: Any = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details: list[dict] = _coerce_details(details)
        self.schema_reconciliation: dict | None = (
            schema_reconciliation if isinstance(schema_reconciliation, dict) else None
        )
        # Structured fail-closed diagnostics (feature-sdk-dx item 3). Read off
        # the error body when present; default to empty/None otherwise.
        self.missing_atoms: list = list(missing_atoms) if isinstance(missing_atoms, list) else []
        self.deciding_rule: Any = deciding_rule
        self._rejected_facts_explicit: list | None = (
            list(rejected_facts) if isinstance(rejected_facts, list) else None
        )
        self.stalled_stage: Any = stalled_stage
        detail_str = _format_details(self.details)
        full = f"{message} ({detail_str})" if detail_str else message
        super().__init__(full)

    @property
    def rejected_facts(self) -> list:
        """The facts the verified engine rejected (may be empty).

        Prefers the explicit ``rejected_facts`` list off the error body — the
        structured :class:`~ambertraceai.responses.RejectedFact` shape
        (``{field, value, reasons}``) the platform emits on a fail-closed 503
        (#652). Falls back to the bare ``field`` names carried in ``details``
        for back-compatibility with a pre-#652 deployment (which surfaced only
        the ``details`` FieldError block).
        """
        if self._rejected_facts_explicit is not None:
            return self._rejected_facts_explicit
        return [d["field"] for d in self.details if d.get("field")]

    @property
    def unmappable_fields(self) -> list[str]:
        """The field references the column-mapping gate rejected (may be empty).

        Populated on a ``schema_conflict`` (HTTP 400) from a rule create/edit —
        the ``field`` of each entry in ``schema_reconciliation.conflicts``.
        """
        recon = self.schema_reconciliation or {}
        return [
            c["field"] for c in recon.get("conflicts", [])
            if isinstance(c, dict) and c.get("field")
        ]


# --- Cold-start resilience -------------------------------------------------
#
# The platform runs scale-to-zero (the machine suspends when idle and is woken
# by incoming traffic). During the wake / rolling-restart window Fly's proxy has
# no healthy instance yet and returns a 5xx WITHOUT the app's JSON envelope (or
# the connection fails outright). The SDK rides over that window transparently
# so callers don't see spurious failures — while NEVER masking a real app
# response: a deliberate verified-profile fail-closed 503 (which carries the
# app's ``{"error": ...}`` envelope) is surfaced immediately, not retried.
_RETRY_STATUSES = frozenset({502, 503, 504})
_MAX_RETRIES = 5            # retries after the first attempt
_BASE_DELAY = 0.5           # seconds
_MAX_DELAY = 8.0
_HEALTH_PATH = "/ambertrace/health"

# The API is served from ``app.ambertrace.ai``. A common mistake is to point
# ``base_url`` at ``api.ambertrace.ai``, which is not an API endpoint and fails
# with an opaque Cloudflare 525 TLS error — so we reject it up front with a
# clear message rather than letting the user debug a handshake failure.
_API_HOST = "app.ambertrace.ai"
_WRONG_API_HOST = "api.ambertrace.ai"

# Environment-variable names + the production default base URL, used by
# :meth:`AmbertraceAPI.from_env` and the constructor's env fallbacks so callers
# don't re-implement auth boilerplate (feature-sdk-dx item 7).
_ENV_API_KEY = "AMBERTRACE_API_KEY"
_ENV_BASE_URL = "AMBERTRACE_BASE_URL"
_DEFAULT_BASE_URL = f"https://{_API_HOST}"


def _load_dotenv(path: str) -> dict[str, str]:
    """Parse a ``.env`` file into a dict (no third-party dependency).

    Supports ``KEY=value`` lines, ``export KEY=value``, ``#`` comments, blank
    lines, and single/double-quoted values. Returns ``{}`` when the file is
    absent or unreadable (best-effort — never raises). Does NOT mutate
    ``os.environ``; the caller decides precedence.
    """
    values: dict[str, str] = {}
    try:
        with open(path, encoding="utf-8") as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("export "):
                    line = line[len("export "):].lstrip()
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                val = val.strip()
                if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
                    val = val[1:-1]
                if key:
                    values[key] = val
    except OSError:
        return {}
    return values


def _is_wrong_api_host(base_url: str) -> bool:
    """True iff ``base_url``'s host is the known-wrong ``api.ambertrace.ai``.

    Robust to a missing scheme (``api.ambertrace.ai`` parses with no netloc),
    an explicit port, and case. Any other host — including arbitrary custom or
    self-hosted endpoints — returns False and constructs normally.
    """
    parsed = urllib.parse.urlparse(base_url)
    # Without a scheme, urlparse puts the host in ``path``; reparse with one.
    host = parsed.hostname or urllib.parse.urlparse(f"//{base_url}").hostname
    return (host or "").lower() == _WRONG_API_HOST


def _backoff_delay(attempt: int) -> float:
    """Exponential backoff with jitter for the ``attempt``-th retry (0-based)."""
    base = min(_MAX_DELAY, _BASE_DELAY * (2 ** attempt))
    return base + random.uniform(0, base * 0.25)


def _parse_envelope(resp: httpx.Response):
    """Return ``(body, is_envelope)``. ``is_envelope`` is True when the response
    is the app's JSON object envelope (``{"data": ...}`` / ``{"error": ...}``) —
    i.e. a genuine app response, as opposed to a Fly proxy 5xx (HTML/empty) seen
    while the backend is waking."""
    try:
        body = resp.json()
    except Exception:
        return None, False
    return (body, True) if isinstance(body, dict) else (body, False)


class _Resource:
    def __init__(self, client: httpx.Client):
        self._http = client

    def _request(self, method: str, path: str, **kwargs) -> Any:
        attempt = 0
        while True:
            try:
                resp = self._http.request(method, path, **kwargs)
            except httpx.TransportError as exc:
                # No response — the machine is almost certainly waking from
                # suspend (the proxy rejects before routing, so even a POST has
                # not reached the app). Retry over the wake window.
                if attempt >= _MAX_RETRIES:
                    raise AmbertraceError(
                        503, "backend_unavailable",
                        f"backend unreachable after {attempt + 1} attempt(s): {exc}",
                    ) from exc
                time.sleep(_backoff_delay(attempt))
                attempt += 1
                continue

            body, is_envelope = _parse_envelope(resp)

            # Infra/proxy 5xx WITHOUT the app envelope = no healthy instance yet
            # (waking / rolling restart). Retry. A 5xx WITH the envelope is a
            # real app response (e.g. verified fail-closed 503) — fall through.
            if resp.status_code in _RETRY_STATUSES and not is_envelope:
                if attempt >= _MAX_RETRIES:
                    raise AmbertraceError(
                        resp.status_code, "backend_unavailable",
                        f"backend unavailable after {attempt + 1} attempt(s) "
                        f"(HTTP {resp.status_code})",
                    )
                time.sleep(_backoff_delay(attempt))
                attempt += 1
                continue

            if resp.status_code >= 400:
                err = body.get("error", {}) if isinstance(body, dict) else {}
                if not isinstance(err, dict):
                    err = {}
                top = body if isinstance(body, dict) else {}

                # Structured fail-closed query diagnostics (feature-sdk-dx item
                # 3). The platform may attach these either inside ``error`` or at
                # the top level of the body — read whichever is present so the
                # pass-through is robust to the eventual server placement.
                def _pick(key: str) -> Any:
                    v = err.get(key)
                    return v if v is not None else top.get(key)

                raise AmbertraceError(
                    resp.status_code,
                    err.get("code", "unknown"),
                    err.get("message", resp.text),
                    err.get("details"),
                    # Data-driven ontology (D1): a schema_conflict 400 carries the
                    # column-mapping report at the top level of the error body.
                    top.get("schema_reconciliation"),
                    missing_atoms=_pick("missing_atoms"),
                    deciding_rule=_pick("deciding_rule"),
                    rejected_facts=_pick("rejected_facts"),
                    stalled_stage=_pick("stalled_stage"),
                )
            return body.get("data", body) if isinstance(body, dict) else body


class DomainResource(_Resource):
    def list(self) -> list[DomainOut]:
        return self._request("GET", "/api/v1/domains")

    def create(self, *, name: str, description: str, **kwargs) -> DomainOut:
        return self._request("POST", "/api/v1/domains", json={"name": name, "description": description, **kwargs})

    def get(self, domain_id: int) -> DomainOut:
        """Return the full domain detail including the ontology.

        The ``ontology`` dict on the response carries the built rule set and,
        when a stated constraint from the domain description is not encoded by
        any rule, a ``stated_constraint_diagnostics`` list of
        :class:`~ambertraceai.responses.StatedConstraintFinding` dicts.
        This diagnostic is advisory (it never gates the build) and only appears
        when there are unencoded constraints to report.
        """
        return self._request("GET", f"/api/v1/domains/{domain_id}")

    def update(self, domain_id: int, **kwargs) -> DomainOut:
        return self._request("PUT", f"/api/v1/domains/{domain_id}", json=kwargs)

    def delete(self, domain_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/domains/{domain_id}")

    def build_ontology(self, domain_id: int, *, relations: list[dict] | None = None) -> dict:
        """Build the domain's ontology + rules from its description and data.

        A dataset is REQUIRED: upload data to the domain first (the canonical
        flow is create domain -> upload data -> build_ontology). Rules are
        authored against the real data columns, and every field reference is
        validated to map to a column (or an in-set derived concept) at creation
        time; an unmappable reference fails the build rather than producing a
        rule that can never fire. Calling without a dataset returns HTTP 400.
        Returns a 202 job envelope (an :class:`AttrDict`) carrying a stable
        ``job_id`` -- poll the job until it completes (``api.wait_for_job(
        onto.job_id)``).

        ``relations`` (optional) declares certified RELATIONS for Tier-1
        cross-domain cueing — a decision that depends on whether a related record
        exists, with the join brought INSIDE the proof. Each entry is
        ``{"name": str, "join_key": str, "columns": [{"name": str, "type":
        "string|enum|bool|float|int", "enum_values"?: [...]}]}``. With a relation
        declared, a description clause like *"X when there exists a related
        <name> in the same <join_key> whose <col> is <val>"* is authored as an
        ``existsRelated`` derive rule grounded against the declared relation
        schema. Attached rows are then supplied per query via
        ``platforms.query(..., relations={name: [row, ...]})`` and folded in the
        proof; matched rows surface in ``explanation.relation_provenance``.

        N-class / multi-class classifier. A description that defines N
        MUTUALLY-EXCLUSIVE labels (see example 38) builds a verified **N-class /
        multi-class classifier** -- one derived-outcome rule per label; the built
        platform's ``query`` ``decision`` is the WINNING label. This is the ordinary
        ``domains`` -> ``build_ontology`` -> ``platforms.create(verified_profile=
        True)`` -> ``platforms.query`` path -- there is NO ``multiclass``
        ``model_type`` and it is NOT ``author()`` (that is the permit/deny Agent
        Policy Gate). Phrase each axis with a threshold + an ``otherwise`` clause,
        each label as a conjunction of axis states, and state "classified into
        exactly one" for completeness.

        Decision vocabulary (custom decision verbs). The terminal decision VERBS are
        inferred from your description's language -- a description that decides with
        domain-specific verbs (e.g. "clear / monitor / escalate", or the N class
        labels above) DECLARES those as the platform's decision vocabulary, with a
        restrictiveness rank. Read them back on ``query().decision`` /
        ``status().decision_vocabulary``; you are not limited to permit/deny.
        """
        body = {"relations": relations} if relations is not None else None
        return _normalise_envelope(self._request(
            "POST", f"/api/v1/domains/{domain_id}/build-ontology",
            **({"json": body} if body is not None else {})))

    # -- Evaluation config --

    def eval_config(self, domain_id: int) -> dict:
        """The domain's evaluation config (or ``None`` if unset).

        An eval config names the SINGLE domain-level outcome metric a rule
        suggestion / discovery is scored against — so a suggested rule earns its
        place by moving THIS metric, not a generic accuracy proxy. Fields:
        ``target_metric`` (machine-name, e.g. ``"readmission_30d"``), ``direction``
        (``"minimize"`` | ``"maximize"``), ``unit``, ``description``,
        ``significance_threshold_pp`` (min improvement in percentage points to
        count), ``min_positive_fraction``, and an optional ``calculation`` block."""
        return self._request("GET", f"/api/v1/domains/{domain_id}/eval-config")

    def set_eval_config(self, domain_id: int, *, target_metric: str,
                        direction: str, description: str = "", unit: str = "other",
                        significance_threshold_pp: float | None = None,
                        min_positive_fraction: float | None = None,
                        calculation: dict | None = None, **kwargs) -> dict:
        """Set the domain's evaluation config (see :meth:`eval_config`).

        ``target_metric`` (required) is the outcome metric name; ``direction``
        (required) is ``"minimize"`` or ``"maximize"``. ``significance_threshold_pp``
        is the minimum improvement (percentage points) a suggested rule must show to
        be worth adopting; ``min_positive_fraction`` bounds how often the metric's
        positive case must occur; ``calculation`` optionally specifies how the metric
        is computed from columns. Returns the stored config."""
        body: dict[str, Any] = {"target_metric": target_metric,
                                "direction": direction, "description": description,
                                "unit": unit, **kwargs}
        if significance_threshold_pp is not None:
            body["significance_threshold_pp"] = significance_threshold_pp
        if min_positive_fraction is not None:
            body["min_positive_fraction"] = min_positive_fraction
        if calculation is not None:
            body["calculation"] = calculation
        return self._request("PUT", f"/api/v1/domains/{domain_id}/eval-config", json=body)

    def delete_eval_config(self, domain_id: int) -> dict:
        """Remove the domain's evaluation config."""
        return self._request("DELETE", f"/api/v1/domains/{domain_id}/eval-config")

    def suggest_eval_config(self, domain_id: int) -> dict:
        """Ask the platform to SUGGEST candidate eval configs from the domain's data
        + description. Returns ``{"options": [{target_metric, direction, unit,
        description, ...}, ...]}`` — review one and pass it to
        :meth:`set_eval_config`. A convenience for bootstrapping the metric rather
        than hand-naming it."""
        return self._request("POST", f"/api/v1/domains/{domain_id}/eval-config/suggest")

    # -- Rule templates --

    def list_templates(self, domain_id: int) -> list[dict]:
        """List the domain's reusable rule TEMPLATES (parameterised rule shapes a
        suggestor can instantiate). Each is a ``{template_id, name, category,
        condition_field, condition_operator, action_type, ...}`` dict."""
        return self._request("GET", f"/api/v1/domains/{domain_id}/templates")

    def create_template(self, domain_id: int, *, template_id: str, name: str,
                        **kwargs) -> dict:
        """Create a reusable rule template on the domain. ``template_id`` (stable id)
        and ``name`` are required; optional ``category``, ``condition_field``,
        ``condition_operator``, ``action_type`` describe the rule shape."""
        body: dict[str, Any] = {"template_id": template_id, "name": name, **kwargs}
        return self._request("POST", f"/api/v1/domains/{domain_id}/templates", json=body)

    def update_template(self, domain_id: int, template_id: int, **kwargs) -> dict:
        """Update a rule template (pass the fields to change; see
        :meth:`create_template` for the shape)."""
        return self._request("PUT", f"/api/v1/domains/{domain_id}/templates/{template_id}", json=kwargs)

    def delete_template(self, domain_id: int, template_id: int) -> dict:
        """Delete a rule template."""
        return self._request("DELETE", f"/api/v1/domains/{domain_id}/templates/{template_id}")

    def feedback_stats(self, domain_id: int) -> dict:
        return self._request("GET", f"/api/v1/domains/{domain_id}/feedback-stats")


class DatasetResource(_Resource):
    def list(self) -> list[DatasetOut]:
        """List the caller's datasets.

        Each item is an :class:`AttrDict` — subscriptable as before
        (``ds["row_count"]``) and attribute-accessible (``ds.row_count``,
        ``ds.column_count``, ``ds.decision_column``) for IDE autocomplete.
        """
        return [_wrap(d) for d in self._request("GET", "/api/v1/datasets")]

    def get(self, dataset_id: int) -> DatasetOut:
        """Fetch one dataset as an :class:`AttrDict`.

        Exposes the ``DatasetOut`` fields the SDK models document —
        ``id``, ``name``, ``domain_id``, ``status``, ``source_type``,
        ``row_count``, ``column_count``, ``decision_column``, ``schema_info``,
        ``description``, ``created_at``, ``updated_at`` — via both ``[...]`` and
        attribute access, so the fields are discoverable without grepping SDK
        source.
        """
        return _wrap(self._request("GET", f"/api/v1/datasets/{dataset_id}"))

    def upload(self, *, domain_id: int, file_path: str, name: str | None = None,
               decision_column: str | None = None) -> DatasetOut:
        """Upload a CSV/data file and ingest it as a dataset on a domain.

        Returns an :class:`AttrDict` carrying the ``DatasetOut`` fields
        (``id``, ``status``, ``row_count``, ``column_count``,
        ``decision_column``, ...) — readable via ``[...]`` (unchanged) or
        attribute access (``ds.row_count``) for discoverability.

        ``decision_column`` — naming a column here flips the build from
        *features-only* (unsupervised) to **label-supervised**: that column is
        treated as the labelled outcome the platform learns to reach, and
        verdict/decision rule generation is grounded against its observed label
        values rather than inferred from the feature columns alone. Leave it
        unset to build features-only. (See the supervised coverage caveat in
        the platform build diagnostics: a supervised build can leave some
        declared decision classes unreachable — check
        ``generation_diagnostics`` after the build.)
        """
        with open(file_path, "rb") as f:
            files = {"file": (name or file_path.split("/")[-1], f)}
            data = {"domain_id": str(domain_id)}
            if name:
                data["name"] = name
            if decision_column:
                data["decision_column"] = decision_column
            return _wrap(self._request("POST", "/api/v1/datasets/upload", files=files, data=data))

    def fetch(self, *, domain_id: int, connector_type: str, config: dict | None = None) -> DatasetOut:
        """Ingest a dataset from a registered connector.

        Connector types (``connector_type``):

        * **Keyless (public data):** ``yahoo``, ``coinbase``, ``boe``, ``ecb``,
          ``oecd``, ``eurostat``, ``fiscaldata``, ``edgar``, ``worldbank``,
          ``gdelt``, ``sentiment``.
        * **Bring-your-own-key:** ``fred`` / ``fred_sentiment`` (free FRED key,
          ``config["api_key"]``), ``imf`` (IMF iData subscription key,
          ``config["api_key"]`` = ``Ocp-Apim-Subscription-Key``; set
          ``IMF_API_KEY`` in the env), ``rest`` (custom auth via
          ``config["headers"]``).

        ``config`` carries connector-specific options and any bring-your-own-key
        credentials. See ``api.connectors.list()`` for the full list with
        descriptions and required fields.

        ASYNC (like :meth:`fetch_multi`): the network fetch runs in the
        background, so this returns the dataset record (HTTP 202) with
        ``status == "processing"`` — poll :meth:`get` until ``status == "ready"``
        before building an ontology / platform on it (an unready dataset fails the
        build). ``status == "error"`` means the fetch failed.
        """
        body: dict[str, Any] = {
            "domain_id": domain_id,
            "connector_type": connector_type,
            "config": config or {},
        }
        return self._request("POST", "/api/v1/datasets/fetch", json=body)

    def fetch_multi(self, *, domain_id: int, sources: list[dict],
                    join_on: str = "date", frequency: str | None = None,
                    aggregation: str | None = None) -> DatasetOut:
        """Fetch from two or more connectors and MERGE them into ONE date-aligned
        dataset, so a forecaster can train across sources in a single panel.

        ``sources`` is a list of ``{"connector_type": ..., "config": {...}}``
        dicts (at least two), e.g. ``[{"connector_type": "fred", "config":
        {"series_ids": [...], "api_key": ...}}, {"connector_type": "boe",
        "config": {...}}]``. The sources are outer-joined on the ``join_on`` index
        column (default ``"date"``); each value column is namespaced by connector
        type to avoid collisions (e.g. ``boe.IUDSOIA``). Set ``frequency``
        (``daily``/``weekly``/``monthly``/``quarterly``/``annual``) with
        ``aggregation`` (``last`` or ``mean``) to resample mixed-cadence sources
        onto a common grid before joining; without it, mixed-frequency sources
        outer-join to a mostly-null table.

        Like :meth:`fetch`, this always runs asynchronously (network fetch × N):
        the call returns the dataset record (HTTP 202, ``status == "processing"``)
        — poll :meth:`get` until ``status == "ready"`` before building on it. See
        ``api.connectors.list()`` for available connectors and their requirements.
        """
        body: dict[str, Any] = {
            "domain_id": domain_id,
            "join_on": join_on,
            "sources": sources,
        }
        if frequency is not None:
            body["frequency"] = frequency
        if aggregation is not None:
            body["aggregation"] = aggregation
        return self._request("POST", "/api/v1/datasets/fetch-multi", json=body)

    def quality(self, dataset_id: int) -> dict:
        return self._request("GET", f"/api/v1/datasets/{dataset_id}/quality")

    def clean(self, dataset_id: int, *, steps: list[str] | None = None) -> DatasetOut:
        """Clean/normalise a dataset (dedupe, type-coerce, drop-empty, ...).

        ASYNC like :meth:`fetch`: cleaning runs in the background and the dataset
        goes back to ``status == "processing"`` — poll :meth:`get` until
        ``status == "ready"`` before building on the cleaned dataset. ``steps``
        (optional) selects specific cleaning steps; omit for the server defaults.
        """
        # The endpoint expects a JSON body even though all fields default
        # server-side; send {} (or the chosen steps) so validation passes.
        body: dict[str, Any] = {}
        if steps is not None:
            body["steps"] = steps
        return self._request("POST", f"/api/v1/datasets/{dataset_id}/clean", json=body)

    def preview(self, dataset_id: int) -> dict:
        return self._request("GET", f"/api/v1/datasets/{dataset_id}/preview")

    def delete(self, dataset_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/datasets/{dataset_id}")


class PlatformResource(_Resource):
    def list(self) -> list[PlatformOut]:
        return self._request("GET", "/api/v1/platforms")

    def create(self, *, domain_id: int, dataset_id: int, name: str | None = None, **kwargs) -> AttrDict:
        """Create a platform and dispatch its build (async).

        Returns an :class:`AttrDict` whose original shape is preserved
        (``result["platform"]["id"]`` / ``result["build_job"]["id"]`` still
        work) AND which is stamped with a normalised, stable ``id`` (the new
        platform's id) and ``job_id`` (the build job's id), so a caller can do::

            result = api.platforms.create(domain_id=1, dataset_id=2)
            api.wait_for_job(result.job_id)        # or result["job_id"]
            api.platforms.query(result.id, query=...)

        without unwrapping ``build_job.job.id`` / ``platform.id`` by hand
        (feature-sdk-dx item 4).

        Verified-profile build kwargs (ride through ``**kwargs``). This is THE way
        to build a VERIFIED platform (a machine-checked proof per query). Pass:

        * ``verified_profile: bool`` -- build with the verified profile ON (every
          answer carries a checked proof; uncertifiable queries fail closed).
        * ``verified_min_confidence: float`` -- the fact-gate confidence threshold τ
          (e.g. ``0.85``); a fact below τ is not certified.
        * ``invariant_manifest: list[dict]`` -- named invariants the build must
          satisfy (each ``{"name": str, "kind": ..., ...}``); a violated invariant
          fails the build rather than shipping an unsound platform.
        * ``override_verification_gate: bool`` -- explicitly build even if the
          verification gate flags a concern (use sparingly; audited).
        * ``scored_determinations: dict`` -- OPEN-TEXTURED SCORED DETERMINATIONS
          (flag-gated, default OFF). For an OPEN-TEXTURED predicate that bright-line
          rules cannot decide (compatibility / reasonableness / materiality /
          good-faith), the platform's OWN runtime LLM is given rich doctrine + the
          situation TEXT and returns a *calibrated probability* the predicate holds,
          admitted as a confidence-carrying fact subject to τ
          (``verified_min_confidence``): ``p >= τ`` supports a permit;
          ``p < τ`` OR an abstain / out-of-distribution / high self-consistency
          dispersion determination admits NO fact and routes to ``escalate`` (never
          a permit -- deductive-first, fail-closed). The score is SERVER-COMPUTED
          from the text (a caller cannot hand-set it). Shape::

              scored_determinations={
                "enabled": True,
                "determinations": [{
                  "head": "compatibility_established",   # the derived-head field
                  "question": "Is the PROPOSED USE compatible with ...?",
                  "doctrine": "<the legal / domain doctrine -- the tuning surface>",
                  "situation_fields": {                  # prompt label -> request field
                    "ORIGINAL COLLECTION PURPOSE": "collection_purpose",
                    "PROPOSED USE": "stated_purpose"},
                  "dispersion_escalate": 0.15            # optional escalate threshold
                }]}

          The head fact then feeds your ordinary rules (e.g.
          ``permit when compatibility_established``; an ``escalate`` rule keyed on
          its absence catches the sub-τ / uncertified case). See example 41. Its
          guarantee is EMPIRICAL (calibration-in-regime + coherent-input +
          fail-closed-OOD) -- honestly WEAKER than the deductive kernel proofs.

        Example::

            api.platforms.create(domain_id=1, dataset_id=2, verified_profile=True,
                                  verified_min_confidence=0.85)

        (These are also settable post-hoc via :meth:`update`; see examples 10/11/14.)
        For an N-class / MULTI-CLASS classifier, build a verified platform this way
        over a domain whose description declares N mutually-exclusive labels -- see
        :meth:`DomainResource.build_ontology` and example 38 (it is NOT ``author()``).
        """
        body: dict[str, Any] = {"domain_id": domain_id, "dataset_id": dataset_id, **kwargs}
        if name:
            body["name"] = name
        return _normalise_envelope(self._request("POST", "/api/v1/platforms", json=body))

    def get(self, platform_id: int) -> PlatformOut:
        return self._request("GET", f"/api/v1/platforms/{platform_id}")

    def build_quality(self, platform_id: int) -> BuildQuality | None:
        """The platform's persisted build-quality block, or ``None`` if it has
        not been built yet.

        The block is the customer-facing summary of the build's STRUCTURAL
        health — the honest, label-free substitute for an accuracy number,
        which can't transfer to your domain. Shape::

            {"status": "ok" | "warnings" | "needs_review",
             "checks": [{"id": str,
                         "severity": "blocking" | "warning" | "info",
                         "ok": bool, "detail": str, "items": [str, ...]}, ...]}

        ``status`` is ``needs_review`` whenever any *blocking* check fails — the
        platform cannot reach a declared decision class, or
        it has no restrictive (deny / block) decision and so permits everything.
        Use :meth:`blocking_checks` to get just the failing blocking checks, or
        read ``build_quality`` straight off the build job result (see
        :meth:`AmbertraceAPI.wait_for_job`)."""
        platform = self.get(platform_id)
        return platform.get("build_quality")

    def blocking_checks(self, platform_id: int) -> list[BuildQualityCheck]:
        """The FAILING blocking checks for a built platform — empty when the
        build has no blocking problems (or has not been built). Each item is a
        check dict from :meth:`build_quality`."""
        bq = self.build_quality(platform_id)
        if not isinstance(bq, dict):
            return []
        return [
            c for c in (bq.get("checks") or [])
            if isinstance(c, dict)
            and c.get("severity") == "blocking" and not c.get("ok")
        ]

    def delete(self, platform_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/platforms/{platform_id}")

    def status(self, platform_id: int) -> PlatformStatusOut:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/status")

    def query(self, platform_id: int, *, query: str, explain: bool = True,
              facts: dict | None = None,
              # {role: {"model_id", "as_of", "mode": "fatal"|"non_fatal"}}
              predictions: dict[str, dict[str, str | None]] | None = None,
              relations: dict[str, list[dict]] | None = None,
              top_k: int = 10,
              **kwargs) -> QueryResult:
        """Query a platform; returns ``{answer, decision, explanation, ...}``.

        ``facts`` (``{field: scalar}``) is the FOCAL row. On a verified platform
        these ARE the certified EDB — each is certified through the fact gate
        (declared in the domain schema, in-domain, ground); neural retrieval is
        not consulted for the fact base, so a fully-specified request decides
        deterministically.

        ``predictions`` (``{role: {"model_id": str, "as_of": str|None,
        "mode": "fatal"|"non_fatal"}}``) is the native, FAIL-CLOSED
        Prediction -> Decision fan-in: reference one or more
        VERIFIED forecasts this org (org+owner-scoped) already produced +
        persisted, by ``model_id`` + alignment ``as_of`` — and the platform folds
        each referenced forecast's CERTIFIED fields into the decision's certified
        EDB for you. PREFER this over passing a forecast number in ``facts`` (see
        the by-reference contract below).

        BY REFERENCE, never by value. You supply only the reference
        (``model_id``/``as_of``); the platform fetches the stored
        ``prediction_record`` and admits ONLY its certified fields keyed
        ``<role>.<field>``: ``<role>.value`` (the LEVEL-space point forecast),
        ``<role>.probability`` (ONLY if the record's probability certified), and a
        ``<role>.fired.<signal>`` boolean per fired driver signal. A rule reading
        ``<role>.value`` / ``<role>.probability`` then decides over TRUSTED facts.
        The caller never supplies the forecast value — that is the safety property:
        the forecast's certificate certifies its INPUT ROW, not that the emitted
        value follows, so the platform (not the caller) is the source of the number.

        FAIL-CLOSED (the escalate-safe contract). A reference that is (a) missing /
        out-of-scope, (b) whose forecast is not ``proof_checked``, (c) whose stored
        ``as_of`` != the requested ``as_of``, or (d — for the probability fact only)
        whose probability was not certified, admits NO affected fact. A forecast is
        ``proof_checked`` / ``probability_certified`` only when it was produced with
        a certified in-domain input and an in-regime calibration
        (``symbolic_forecast(verified=True)``) — so a forecast whose input row or
        probability did not clear the model's confidence gate is stamped
        NOT-certified AT PRODUCTION TIME and therefore admits no fact here. With the
        fact absent, a rule reading ``<role>.<field>`` cannot fire a certified
        permit, so the decision ABSTAINS — a policy that has an ``escalate`` /
        ``refer`` fallback routes there rather than approving on an uncertified or
        low-confidence forecast. The response's ``proof_checked`` is True IFF the
        decision certifies AND every referenced prediction was found + aligned +
        certified. Verified platforms only. The PRODUCING method is
        :meth:`PredictionResource.symbolic_forecast` — name + ``as_of``-stamp the
        record there (``prediction_name`` / ``prediction_model_id`` / ``as_of``) so
        it is addressable here.

        PER-REFERENCE ``mode`` — graceful escalate vs. hard fail-closed. Each
        reference may carry ``"mode"``:

        * ``"fatal"`` (the DEFAULT — omit ``mode`` to get it) — a reference that
          fails the gate fails the WHOLE query closed (HTTP 503, no decision). This
          is the strict fail-closed composition above; every existing caller keeps it.
        * ``"non_fatal"`` — a reference that fails the gate admits NO fact (as
          always) but the query PROCEEDS and decides over what remains, so a
          lower-precedence ``escalate`` / ``deny`` rule can fire on the ABSENCE of
          the basis and return a certified ``200`` (e.g. "if the referenced
          determination isn't certified, escalate to a human" instead of 503-ing).

        ``non_fatal`` does NOT relax the safety guarantee. A permit still can never
        rest on the absence of an uncertified reference: the verified kernel's
        permit-guard DROPS any permit whose firing depends — directly or
        through a derive chain — on a negation-as-failure over an uncertified key
        (e.g. ``permit when compatibility ne "incompatible"`` over an uncertified
        ``compatibility`` can NOT certify). A missing basis is BLOCKING for any
        permit but AVAILABLE-AS-ABSENCE for an explicit escalate/deny fallback. The
        uncertified reference and any guarded-out permit are surfaced in
        ``explanation["rejected_facts"]`` and ``explanation["graceful_escalate"]``
        (``{uncertified_roles, permits_dropped}``) so the escalate is explainable.
        The only thing ``non_fatal`` buys is "route the absence to my escalate/deny
        rule instead of 503."

        Example (graceful escalate on an uncertified reference)::

            api.platforms.query(
                records_pid,
                query="Decide the records disclosure.",
                facts={"routine_use_claimed": True},
                predictions={"compatibility":
                             {"model_id": "compat_score", "as_of": "2026-06-30",
                              "mode": "non_fatal"}},
            )
            # if `compatibility` is missing / uncertified / mis-aligned, the query
            # does NOT 503: the permit that would rest on its absence is guarded out
            # and the `escalate when routine_use_unverified` fallback certifies a
            # 200 escalate; the uncertified reference is in explanation.rejected_facts.

        Example (native by-reference fan-in — no caller-supplied forecast value)::

            api.platforms.query(
                loan_pid,
                query="What is the lending decision?",
                facts={"credit_score": 700, "debt_to_income_ratio": 0.30},
                predictions={"forecast_credit_spread":
                             {"model_id": "ig_spread", "as_of": "2026-06-30"}},
            )
            # a rule reading `forecast_credit_spread.value` decides over the
            # platform-produced, certified forecast — if that forecast is missing /
            # uncertified / mis-aligned the fact is absent and the decision abstains.

        ``top_k`` (default 10, 1..50) bounds how many neural-evidence items the
        retrieval layer returns for the answer narrative. It does NOT affect the
        certified fact base on a fully-specified verified query (``facts`` /
        ``predictions`` are the EDB); tune it only for the narrative / non-verified
        retrieval breadth.

        ``relations`` (``{relation_name: [ {column: scalar}, ... ]}``) attaches
        RELATED FACTS alongside ``facts`` so the verified kernel can bring a
        relational / cross-domain join INSIDE the proof (Tier-1
        cross-domain cueing). A ``derive`` rule whose condition is an aggregate
        (``count``/``sum``) or an existential (``existsRelated``) leaf folds over
        the certified related rows — joined on the declared join key — and its
        derived flag feeds the decision. Every row is certified per-cell at the
        platform's confidence threshold; if ANY row is rejected the whole query
        fails CLOSED (no decision over a partial relation). When an existential
        cue fires, the matched related rows are surfaced in
        ``explanation["relation_provenance"][<derived_field>] =
        {relation, matched, min_count, count}`` (audit-only; never affects the
        decision). Verified platforms only.

        Example (bring a cross-domain join inside the proof)::

            api.platforms.query(
                pid,
                query="Triage this track.",
                facts={"identification": "unidentified", "grid_square": "G3"},
                relations={"maritime_track": [
                    {"grid_square": "G3", "zone_status": "exclusion_breach",
                     "ais_corroborated": True},
                ]},
            )
            # the platform's existsRelated rule ("maritime-cued when there exists a
            # related maritime_track in the same grid_square whose zone_status is
            # exclusion_breach and ais_corroborated is true") derives the cue from
            # the attached rows — no pre-joined boolean in `facts`.

        Dense-reward / audit consumers (e.g. ``ambertrace-rlvr``): when
        ``explain`` is True the ``explanation`` is a DOCUMENTED, VERSIONED trace
        (typed as :class:`~ambertraceai.QueryExplanation`) you can compute a
        partial-credit reward from without reverse-engineering the response:

        * ``explanation["schema_version"]`` (int) — pin/validate against it
          (currently 1; bumped on any breaking shape change).
        * ``explanation["symbolic_trace"]["rules"]`` — the per-criterion firing
          list (typed :class:`~ambertraceai.RuleFiring`). BOTH fired and unfired
          rules are listed. Per rule: ``rule_name`` (stable id), ``fired`` (on a
          VERIFIED platform this reflects the trusted kernel's CERTIFIED firing
          set, reconciled against ``proof.firings``, not a self-report),
          ``rule_type``, ``action_type``, ``required`` (True for a hard
          obligation — a ``require`` leaf or a deny-family verdict — vs a
          supporting/informational rule), and ``explanation``.
        * ``explanation["certified_facts"]`` / ``["certified_fact_summary"]`` —
          the accepted-fact records + counts (fact provenance for a
          rejected-fact penalty); ``["rejected_facts"]`` for what was bounced.
        * ``explanation["confidence"]`` / ``["proof"]`` — fused confidence and the
          machine-checked derivation certificate.

        ``proof_checked`` guarantee: on a VERIFIED platform a 200 always carries
        ``proof_checked`` True (an uncertifiable verified query fails closed with
        HTTP 503 — it never returns ``proof_checked`` False); on a NON-verified
        platform ``proof_checked`` is ``None``. Treat absent/``None``/``False`` as
        "not certified" (fail-closed).

        Example (dense reward)::

            res = api.platforms.query(pid, query="Classify this variant: ...",
                                      facts={"pvs1": True, "pm2": True},
                                      explain=True)
            for r in res["explanation"]["symbolic_trace"]["rules"]:
                # r == {"rule_name": "pvs1_rule", "fired": True,
                #       "required": True, "rule_type": "constraint", ...}
                ...

        **Org-capability gating.** This endpoint requires the ``query``
        capability to be enabled for the caller's organisation. If the
        capability is disabled, the endpoint returns HTTP 403 with error code
        ``capability_disabled`` and a top-level ``capability`` field naming the
        gated capability (``"query"``). Discover your org's effective set via
        ``GET /api/v1/capabilities`` (user-scoped / session callers only;
        platform-scoped keys receive 403 ``forbidden`` on that endpoint --
        have an org administrator communicate the capability set, or use a
        user-scoped key for discovery).
        """
        body: dict[str, Any] = {"query": query, "explain": explain,
                                "top_k": top_k, **kwargs}
        if facts is not None:
            body["facts"] = facts
        if predictions is not None:
            body["predictions"] = predictions
        if relations is not None:
            body["relations"] = relations
        return self._request("POST", f"/api/v1/platforms/{platform_id}/query", json=body)

    def suggest_rules(self, platform_id: int, *, max_suggestions: int = 5) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/suggest-rules", json={"max_suggestions": max_suggestions})

    def list_suggestions(self, platform_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/suggestions")

    def approve_suggestion(self, platform_id: int, suggestion_id: int) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/suggestions/{suggestion_id}/approve")

    def reject_suggestion(self, platform_id: int, suggestion_id: int) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/suggestions/{suggestion_id}/reject")

    def update(self, platform_id: int, **kwargs) -> dict:
        """Update a platform's verified-profile settings.

        Accepted fields: ``verified_profile``, ``verified_min_confidence``,
        ``invariant_manifest``.  Enabling the verified profile re-validates
        existing active rules and may raise :class:`AmbertraceError` (409).
        """
        return self._request("PATCH", f"/api/v1/platforms/{platform_id}", json=kwargs)

    def graph(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/graph")

    def rule_impact(self, platform_id: int, *, rule_name: str) -> dict:
        """Impact analysis: which live decisions depend on this rule?

        The rule is identified by **name** (not by numeric rule ID). This
        matches the ``rule_edit_gate`` convention used by the verified rule
        engine, where rules are keyed by name within a platform. Note that
        :meth:`update_rule` and :meth:`delete_rule` take a numeric
        ``rule_id`` -- the ``rule_name`` here is the ``name`` field of the
        rule object those methods operate on.

        Returns a dict with ``rule_name``, ``decisions`` (list of decision
        nodes with properties including ``audit_log_id``, ``proof_checked``,
        ``query``), and ``total`` (count).

        Decision nodes are materialized incrementally as queries are made
        against the platform. A newly built platform will have no decision
        nodes until its first query.

        .. code-block:: python

            impact = api.platforms.rule_impact(pid, rule_name="income_check")
            print(f"{impact['total']} decisions depend on this rule")
            for d in impact["decisions"]:
                print(f"  - {d['label']} (proof_checked={d['properties']['proof_checked']})")
        """
        return self._request(
            "GET", f"/api/v1/platforms/{platform_id}/graph/rule-impact",
            params={"rule_name": rule_name},
        )

    def decision_provenance(self, platform_id: int, decision_node_uuid: str) -> dict:
        """Audit navigation: provenance subtree for a decision.

        Returns the decision node and all nodes it derived from (rules,
        datasets, forecasts) via ``derived_from`` edges. Used for compliance
        review and audit navigation.

        The ``decision_node_uuid`` is the ``node_uuid`` of a decision node
        in the platform's knowledge graph. Decision nodes are created
        automatically when queries are made; use :meth:`graph` with
        ``node_type='decision'`` to list them.

        .. code-block:: python

            prov = api.platforms.decision_provenance(pid, "abc-uuid-123")
            print(f"Decision: {prov['decision']['label']}")
            for item in prov["provenance"]:
                print(f"  <- {item['relation_type']}: {item['node']['label']}")
        """
        return self._request(
            "GET", f"/api/v1/platforms/{platform_id}/graph/provenance/{decision_node_uuid}",
        )

    # -- Rules CRUD --

    def list_rules(self, platform_id: int, *, include_inactive: bool = False) -> list[dict]:
        params = {"include_inactive": "true"} if include_inactive else {}
        return self._request("GET", f"/api/v1/platforms/{platform_id}/rules", params=params)

    def create_rule(self, platform_id: int, *, name: str, condition: dict,
                    action: dict, description: str | None = None,
                    is_active: bool = True, priority: int | None = None) -> dict:
        """Create a symbolic rule on a platform.

        Every input-field reference in ``condition`` is validated against the
        domain's dataset columns (data-driven ontology §2.3): a reference that
        maps to no real column (or in-set derived concept) is rejected with
        :class:`AmbertraceError` (HTTP 400, ``code == "schema_conflict"``) — the
        error's :attr:`~AmbertraceError.schema_reconciliation` /
        :attr:`~AmbertraceError.unmappable_fields` name the offending field(s),
        and the rule is NOT created. If the rule references fields but the
        domain has no dataset attached, the error code is ``data_required``.

        On success the returned rule carries a ``schema_reconciliation`` report
        (``{status: 'ok', augmented: [{rule, from, to}], conflicts: []}``)
        listing how each field reference mapped to a real column.
        """
        body: dict[str, Any] = {
            "name": name, "condition": condition, "action": action,
            "is_active": is_active,
        }
        if description is not None:
            body["description"] = description
        if priority is not None:
            body["priority"] = priority
        return self._request("POST", f"/api/v1/platforms/{platform_id}/rules", json=body)

    def update_rule(self, platform_id: int, rule_id: int, **kwargs) -> dict:
        """Patch a rule's fields (only those provided are applied).

        When the patch changes ``condition``, every input-field reference is
        re-validated against the domain's dataset columns (data-driven ontology
        §2.3): an unmappable reference is rejected with :class:`AmbertraceError`
        (HTTP 400, ``code == "schema_conflict"`` — see
        :attr:`~AmbertraceError.schema_reconciliation` /
        :attr:`~AmbertraceError.unmappable_fields`) and the rule is left
        unchanged; if it references fields but no dataset is attached, the code
        is ``data_required``. On success the returned rule carries a
        ``schema_reconciliation`` report when the condition changed.
        """
        return self._request("PATCH", f"/api/v1/platforms/{platform_id}/rules/{rule_id}", json=kwargs)

    def delete_rule(self, platform_id: int, rule_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/platforms/{platform_id}/rules/{rule_id}")

    # -- Drift monitoring --

    def capture_drift_baseline(self, platform_id: int) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/drift/baseline")

    def check_drift(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/drift/check")


class PredictionResource(_Resource):
    def predict(self, platform_id: int, *, prediction_config_id: int,
                feature_overrides: dict | None = None, explain: bool = True) -> PredictResult:
        """Run a prediction with a trained config.

        For a ready-to-persist, always-LEVEL-space record with a certified
        probability, prefer :meth:`symbolic_forecast`'s ``prediction_record``
        (the canonical Stage-A output). ``predict`` returns the neural/backtest
        point forecast: since 1.0.0 ``prediction.value`` is the LEVEL by default,
        but on the no-history path it can be a raw change
        (``prediction.value_space == "transformed_unreconstructed"``) — check
        ``value_space`` before storing ``value`` as a level.

        ``feature_overrides`` is an optional dict of what-if feature values
        (e.g. {"inflation": 5.0}); omit it to predict from the latest data. For
        timeseries configs a raw-column override is injected into the most-recent
        point and the engineered features the model consumes (lags / rolling /
        rate-of-change) are recomputed from it, so the forecast actually moves.
        Any override key that maps to no model-consumed feature is returned in
        the response's ``unmatched_overrides`` list (and ignored), so a what-if
        that could not be applied is visible rather than a silent no-op.

        Since ``1.0.0`` the ``prediction`` object returns ``value`` in LEVEL
        space by default — for a differenced target ``value`` is the
        reconstructed level (``baseline + change``), NOT the raw
        month-over-month change. The change is exposed alongside as
        ``value_change`` so you can read either without a second transform:

        * ``value`` — the point forecast as a LEVEL (the natural space);
        * ``value_change`` — the modelled CHANGE alongside the level (``null``
          for a non-differenced target). For the reconstructable path
          ``value == baseline + value_change`` holds by construction;
        * ``value_space`` — ``"level"`` when ``value`` is a level (no transform,
          or a difference reconstructed back to the level; the common case), or
          ``"transformed_unreconstructed"`` when it is a raw CHANGE that could not
          be reconstructed to a level (a difference transform with no base
          history) — treat that as unreliable, not the level;
        * ``target_transform`` — the EFFECTIVE (post-``auto``-resolution)
          transform applied at train time;
        * ``baseline`` — the level used to reconstruct a differenced forecast
          (``null`` when not applicable).

        .. versionchanged:: 1.0.0
            ``value`` is now the reconstructed LEVEL by default for a differenced
            target (was the raw change); the change moved to ``value_change``.

        **Org-capability gating.** Requires the ``predictions`` capability.
        Returns 403 ``capability_disabled`` when disabled for the org (see
        ``GET /api/v1/capabilities``).
        """
        body: dict[str, Any] = {"prediction_config_id": prediction_config_id, "explain": explain}
        if feature_overrides is not None:
            body["feature_overrides"] = feature_overrides
        return self._request("POST", f"/api/v1/platforms/{platform_id}/predict", json=body)

    def list_configs(self, platform_id: int) -> list[PredictionConfigOut]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/prediction-configs")

    def create_config(self, platform_id: int, **kwargs) -> PredictionConfigOut:
        """Create a prediction config on a platform.

        Pass the config fields as keyword args. ``target_field`` (the column to
        predict) is always required.

        ``mode`` — the PRIMARY switch, and the one to set FIRST; it decides the
        entire mental model, and ``feature_overrides`` on :meth:`predict` means
        something different in each:

        * ``mode="cross_sectional"`` — each ROW is an independent example (no
          time index). The model learns ``target_field`` from the other feature
          columns on the same row. No ``time_index_field`` / ``horizon`` /
          ``frequency`` are needed. On :meth:`predict`, ``feature_overrides`` ARE
          the input row (the feature values to predict from), e.g.
          ``feature_overrides={"inflation": 5.0, "unemployment": 4.0}``.
        * ``mode="timeseries"`` (the default) — rows are an ordered SERIES indexed
          by ``time_index_field`` and forecast ``horizon`` steps ahead at
          ``frequency``. The model consumes engineered lag / rolling /
          rate-of-change features. On :meth:`predict`, ``feature_overrides``
          PERTURB the most-recent point (a what-if injected into the latest row,
          from which the engineered features are recomputed) — it does not supply
          a fresh row.

        Give ``mode`` explicitly so which contract applies is never ambiguous.

        Explanatory-mode forecasting (timeseries mode):

        * ``autoregressive`` — how much the forecast may rely on the TARGET's own
          recent values. ``"full"`` (default — history allowed; the target's own
          lag/rolling/rate-of-change features are available) | ``"limited"``
          (drivers + a little history — only the shortest target-history feature
          is allowed) | ``"none"`` (drivers only — no target-derived
          lag/roc/rolling features at all, so the model and the symbolic rules
          explain the target through your other indicators). Covariate (driver)
          features are never restricted. The effective setting is echoed back in
          the config and in ``predict(...)["explanation"]["model"]``
          (``autoregressive`` / ``max_ar_lag``).
        * ``max_ar_lag`` — advanced numeric override for ``autoregressive``: ``0``
          = drivers only, ``k`` = allow target-history features with
          lag/window/period <= ``k``. Overrides the enum when set.

        Metrics (read off ``predict(...)["explanation"]["model"]["metrics"]``):
        when a
        ``target_transform`` (difference / pct-change / log-diff) is applied, the
        ``metrics`` block reports THREE views so no single number misleads:
        ``transformed`` ({r2, rmse, mae} on the modelled change — the hard part),
        ``level`` ({r2, rmse, mae} on the reconstructed level — what you track,
        rebuilt from the realized previous level for a 1-step backtest), and
        ``skill_vs_persistence`` (level-space — the part the model adds over
        predicting last value), plus ``target_transform``. With no transform,
        ``transformed == level`` (backward compatible).

        The returned config (and every :meth:`list_configs` entry) echoes the
        resolved output space so you learn it WITHOUT predicting:
        ``resolved_target_transform`` + ``output_space`` (``"level"`` vs
        ``"change"``) + ``target_transform_reason``. When a concrete
        ``target_transform`` was given these are populated immediately; when
        ``"auto"`` was requested the transform resolves at TRAIN time, so before
        training they read ``"auto (resolved at train time)"`` and reflect the
        concrete resolved transform once the config is trained.
        """
        return self._request("POST", f"/api/v1/platforms/{platform_id}/prediction-configs", json=kwargs)

    def delete_config(self, platform_id: int, config_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/platforms/{platform_id}/prediction-configs/{config_id}")

    def train(self, platform_id: int, config_id: int, *,
              wait: bool = True,
              timeout: float = 600.0,
              poll_interval: float = 5.0) -> PredictionConfigOut:
        """Train (build) the model for a prediction config (async, HTTP 202).

        By DEFAULT (``wait=True``, since ``1.0.0``) the SDK polls the training job
        to completion — the SAME machinery :meth:`discover_prediction_rules` and
        :meth:`neurosymbolic_comparison` use — and returns the SETTLED trained
        :class:`PredictionConfig` dict, so you don't hand-roll
        poll-then-``list_configs``-and-match-by-id. The returned config reflects the
        resolved ``target_transform`` / ``output_space`` (echoed once trained).

        Pass ``wait=False`` (the escape hatch) to get the raw 202 job envelope
        ``{"config_id", "status": "training", "job_id", "poll"}`` unchanged and poll
        the job yourself (e.g. :meth:`AmbertraceAPI.wait_for_job`), then re-fetch the
        config via :meth:`list_configs`.

        .. versionchanged:: 1.0.0
            ``wait`` now defaults to ``True`` (was ``False``), so ``train`` blocks
            until training settles and returns the trained config instead of the job
            envelope — matching its ``discover_prediction_rules`` sibling. Pass
            ``wait=False`` to restore the historical raw-job return.
        """
        resp = self._request(
            "POST",
            f"/api/v1/platforms/{platform_id}/prediction-configs/{config_id}/train")
        if not wait:
            return resp
        job_id = resp.get("job_id")
        if job_id is None:
            return resp
        self._await_job(
            job_id, what=f"Training for config {config_id}",
            timeout=timeout, poll_interval=poll_interval)
        # The training job's result is the model summary, not the config; return
        # the settled config so the caller gets the trained resource directly
        # (resolves the poll-then-refetch boilerplate the consumer reported).
        for cfg in self.list_configs(platform_id):
            if cfg.get("id") == config_id:
                return cfg
        return resp

    def list_predictions(self, platform_id: int) -> list[ForecastOut]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/predictions")

    # -- Neurosymbolic rule discovery + neural-vs-neurosymbolic comparison --
    #
    # These two are ASYNC (HTTP 202): the call kicks off a background job and
    # returns ``{..., "job_id": ..., "poll": ...}``. By default the SDK polls that
    # job to completion and returns its result — pass ``wait=False`` to get the raw
    # 202 envelope back and poll the job yourself via :meth:`AmbertraceAPI.jobs` /
    # :meth:`AmbertraceAPI.wait_for_job` (the SAME job-poll machinery used here).

    # Terminal job statuses — the same set :meth:`AmbertraceAPI.wait_for_job`
    # treats as done, so the SDK has ONE notion of job completion.
    _JOB_TERMINAL = ("ready", "active", "error", "failed", "completed")
    _JOB_FAILED = ("error", "failed")

    def _await_job(self, job_id: int, *, what: str, timeout: float,
                   poll_interval: float) -> Any:
        """Poll a job to a terminal status and return its ``result`` payload.

        Mirrors :meth:`AmbertraceAPI.wait_for_job` (same terminal-status set,
        same :class:`JobResource` getter) — kept here so a resource method can
        poll without a back-reference to the parent client. Raises
        :class:`AmbertraceError` on a failed job and :class:`TimeoutError` if the
        job does not finish within ``timeout``.
        """
        jobs = JobResource(self._http)
        deadline = time.monotonic() + timeout
        while True:
            job = jobs.get(int(job_id))
            status = job.get("status", "")
            if status in self._JOB_TERMINAL:
                if status in self._JOB_FAILED:
                    raise AmbertraceError(
                        500, "job_failed",
                        f"{what} failed (job {job_id}: "
                        f"{job.get('error_message') or status})",
                    )
                result = job.get("result")
                return result if isinstance(result, dict) else job
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"{what} did not complete within {timeout:.0f}s "
                    f"(job {job_id}, last status: {status})"
                )
            time.sleep(poll_interval)

    def discover_prediction_rules(self, platform_id: int, *,
                                  prediction_config_id: int,
                                  max_rounds: int | None = None,
                                  wait: bool = True,
                                  timeout: float = 600.0,
                                  poll_interval: float = 5.0) -> DiscoverySummary:
        """Discover neurosymbolic CORRECTION rules for a trained config (async).

        Analyses the trained model's residuals, proposes corrective
        adjustment/constraint rule candidates (template + LLM), and A/B-tests each
        against the expanding-window backtest. Accepted rules are stored PENDING
        EXPERT APPROVAL (``is_active=False``) — review and activate them via
        :meth:`PlatformResource.update_rule` once you are satisfied. The config
        must already be trained.

        Returns the discovery SUMMARY ``{"prediction_config_id", "total_accepted",
        "total_rejected", "rounds", "converged", "convergence_reason"}`` when
        ``wait`` is True (the default). Then call
        :meth:`discovered_prediction_rules` to read the accepted rules WITH their
        per-rule fire-rate and backtest delta.

        Pass ``wait=False`` to get the raw 202 envelope (``{"job_id", "poll",
        ...}``) and poll the job yourself. Write-scoped: a user-scoped ``at_`` key
        (owner/admin) is required.
        """
        body: dict[str, Any] = {"prediction_config_id": prediction_config_id}
        if max_rounds is not None:
            body["max_rounds"] = max_rounds
        resp = self._request(
            "POST", f"/api/v1/platforms/{platform_id}/discover-prediction-rules",
            json=body)
        if not wait:
            return resp
        job_id = resp.get("job_id")
        if job_id is None:
            return resp
        return self._await_job(
            job_id, what=f"Prediction-rule discovery for config {prediction_config_id}",
            timeout=timeout, poll_interval=poll_interval)

    def discovered_prediction_rules(self, platform_id: int, *,
                                    prediction_config_id: int) -> DiscoveredRules:
        """The rules discovered for a prediction config — each accepted rule WITH
        its per-rule ``fire_rate`` and backtest ``delta`` (why it earns its
        place), plus how many candidates were rejected.

        Returns ``{"platform_id", "prediction_config_id", "accepted_rules":
        [{"id", "name", "description", "rule_type", "condition", "action",
        "priority", "is_active", "fire_rate", "delta", "eval_metric",
        "discovery_round"}, ...], "total_accepted"}``. Call after
        :meth:`discover_prediction_rules` has completed. Accepted rules are pending
        expert approval (``is_active`` reflects that).
        """
        return self._request(
            "GET", f"/api/v1/platforms/{platform_id}/discovered-prediction-rules",
            params={"prediction_config_id": prediction_config_id})

    def neurosymbolic_comparison(self, platform_id: int, *,
                                 prediction_config_id: int,
                                 include_pending: bool = False,
                                 include_series: bool = False,
                                 wait: bool = True,
                                 timeout: float = 600.0,
                                 poll_interval: float = 5.0) -> NeurosymbolicComparison:
        """Compare the neural-only model against the neurosymbolic model — the
        honest "does the symbolic layer earn its place?" backtest (async).

        Runs the SAME expanding-window backtest twice — once with the neural model
        alone, once with the discovered correction rules layered on top — and
        reports the head-to-head accuracy. Returns ``{"platform_id",
        "prediction_config_id", "target", "neural": {"r2", "rmse", "mae", "n"},
        "neurosymbolic": {"r2", "rmse", "mae", "n"}, "delta": {"r2", "rmse"},
        "n_adjustment_rules", "n_constraint_rules", "n_pending_rules", "fire_rate",
        "mode"}`` when ``wait`` is True (the default). ``delta`` is neurosymbolic −
        neural (a positive ``delta.r2`` / negative ``delta.rmse`` means the symbolic
        layer helped).

        Pass ``include_pending=True`` to ALSO apply the accepted-but-pending
        discovered rules read-only — a "what-if" preview of the discovered set
        BEFORE the human approval gate (``is_active`` is never mutated). The result
        then carries ``mode="preview_pending"`` and ``n_pending_rules``; the default
        (``include_pending=False``) scores active rules only (``mode="active"``).

        Pass ``include_series=True`` to ALSO get the per-period head-to-head over
        the SAME held-out backtest points the aggregate metrics are computed from,
        so the comparison can be charted OVER TIME. The result then carries a
        ``series`` list (omitted by default — additive / back-compatible)::

            "series": [
              {"index": <position in the engineered holdout>,
               "time": <ISO-8601 period, when the config has a usable
                        time_index_field — else absent>,
               "actual": <the realised level target>,
               "neural": <the model-only level prediction>,
               "neurosymbolic": <the prediction after the rules are applied>,
               "rule_fired": <True iff applying the rules CHANGED the prediction
                              for that period — i.e. neural != neurosymbolic>},
              ...
            ]

        The series reconciles with the aggregate metrics (it is the same
        computation, not a recompute) and honours ``include_pending`` (the preview
        series applies the pending rules too). Timeseries configs only.

        Pass ``wait=False`` for the raw 202 envelope (``{"job_id", "poll", ...}``)
        to poll the job yourself.
        """
        resp = self._request(
            "GET", f"/api/v1/platforms/{platform_id}/neurosymbolic-comparison",
            params={"prediction_config_id": prediction_config_id,
                    "include_pending": include_pending,
                    "include_series": include_series})
        if not wait:
            return resp
        job_id = resp.get("job_id")
        if job_id is None:
            return resp
        return self._await_job(
            job_id, what=f"Neurosymbolic comparison for config {prediction_config_id}",
            timeout=timeout, poll_interval=poll_interval)

    # -- Prediction "why" layer (preview) --
    #
    # The symbolic forecaster is a STANDALONE, fully-transparent forecasting mode
    # whose structure IS the explanation: forecast = baseline + Σ fired
    # driver-rules over your data's real features, each with a fitted
    # contribution + reliability. With verified=True the active-driver set is
    # proof-carrying. These endpoints are preview-only (server feature flag
    # AMBERTRACE_SYMBOLIC_FORECAST); they raise AmbertraceError(404) when the
    # platform has the feature disabled.

    def symbolic_forecast(self, platform_id: int, *, prediction_config_id: int,
                          feature_overrides: dict | None = None,
                          verified: bool = False,
                          include_fitted_series: bool = False,
                          prediction_name: str | None = None,
                          prediction_model_id: str | None = None,
                          as_of: str | None = None,
                          sector: str | None = None,
                          period: str | None = None,
                          entity: str | None = None,
                          top_drivers_n: int | None = None,
                          compact_certification: bool = True) -> SymbolicForecastResult:
        """Run the symbolic forecaster and return the forecast WITH its WHY.

        Returns ``{"forecast": {"value", "lower", "upper"}, "baseline",
        "skill_vs_persistence", "why": [...], "accepted_drivers": [...]}``.

        Pass ``include_fitted_series=True`` to ALSO get the backtest's per-period
        fitted-vs-actual TIMESERIES under ``fitted_series`` so you can chart actual
        vs the symbolic-rules-fitted forecast over history. Shape::

            {
              "basis": "walk_forward_out_of_sample_one_step",
              "target_field": "...", "horizon": 1, "n_points": N,
              "series": [
                {"index": <date-or-position>, "actual": <observed>,
                 "predicted": <baseline + Σ fired drivers>,
                 "persistence": <predict-last-level baseline>},
                ...
              ]
            }

        This is the SAME walk ``skill_vs_persistence`` is computed from — no extra
        fit. HONEST LABEL: ``basis`` is ``walk_forward_out_of_sample_one_step`` —
        the driver-rules were induced + accepted on the FIT window only and held
        FROZEN across the holdout, so each period's ``predicted`` never saw that
        period's outcome (the rigorous OUT-OF-SAMPLE one-step fit, NOT an in-sample
        fit). ``series`` is empty when there were too few rows to backtest (the
        honest answer, not an error). It is the model's HISTORICAL fit only —
        belief-agnostic, no market priors. Omitted entirely unless you opt in (the
        default response is not bloated).

        ``why`` IS the substantive explanation — the full set of materially-
        contributing driver-rules the model induced + accepted on the holdout (NOT
        only the ones firing on the most-recent row). So ``why`` is non-empty and
        informative even when nothing fires on the latest row (e.g. a mid-range
        macro reading) — the case where it used to come back ``[]``. It is empty
        ONLY when the data admitted no data-fitting driver at all. Each ``why``
        entry carries:

        * ``driver`` — the plain-English rule (``WHEN … THEN <target> moves …``);
        * ``direction`` (``up``/``down``), ``contribution`` / ``effect`` and
          ``band`` — the fitted magnitude;
        * ``fired_on_latest_row`` — whether this driver is ACTIVE NOW (i.e. its
          antecedent holds on the most-recent row). The point forecast moves off
          persistence by the sum of the contributions of the drivers that are
          active now AND in the composed set (``excluded_from_composed_point`` is
          False);
        * ``base_features`` — the HUMAN-NAMED source feature(s) behind the
          antecedent. When a driver reads an engineered form (e.g.
          ``inflation_rolldev_6``), ``base_features`` maps it back to the ontology
          concept (``["inflation"]``) while ``leaf_features`` / ``is_engineered``
          keep the exact engineered column it reads;
        * ``standalone_holdout_skill`` / ``fire_rate`` / ``reliability`` — the
          data-fit evidence;
        * ``excluded_from_composed_point`` — a driver sound on its OWN
          standalone-skill but kept out of the additive point so the composed sum
          stays coherent (it is still reported here as part of the explanation).

        ``accepted_drivers`` is an ALIAS of ``why`` (the same content, one source
        of truth) retained for backward compatibility. A top-level
        ``max_standalone_holdout_skill`` reports the best standalone-holdout skill
        across the materially-contributing set (the strongest single driver's
        evidence), so you can gauge the explanation's overall strength at a glance.

        Pass ``verified=True`` to run the active-driver set through the verified
        engine — each ``why`` entry that is active now is then stamped
        ``proof_checked`` with its kernel-certified antecedent (drivers not active /
        excluded are honestly left unstamped, fail-closed), and a
        ``why_certification`` block (the certified facts, any rejected facts, the
        proof + summary) is attached. ``feature_overrides`` applies what-if values
        to the most recent row before composing (e.g. ``{"inflation": 5.0}``). The
        config need not be trained — the symbolic forecaster is independent of the
        neural model.

        ``prediction_record`` — THE CANONICAL STAGE-A OUTPUT (always present)
        --------------------------------------------------------------------
        EVERY ``symbolic_forecast`` call (verified or not) also returns a
        top-level ``prediction_record``: a ready-to-persist, bridge-shaped record
        in **LEVEL space** (it is the reconstructed level, e.g. a ``4.32`` yield —
        NOT the change space some raw ``predict()`` paths return, so it resolves the
        value-space question for free). Prefer this over hand-assembling a record
        from ``why`` + ``feature_importance``. Shape::

            {
              "name": <role handle, defaults to target_field>,
              "model_id": <stable id, defaults to name>,
              "as_of": <the forecast period / alignment key, or null>,
              "target_field": "...", "horizon": 1,
              "value": <the LEVEL-space point forecast>,
              "interval": {"lower": ..., "upper": ..., "basis": "backtest_rmse"},
              "probability": <calibrated float in (0,1), or null if uncertified>,
              "probability_certified": <bool>,
              "probability_basis": { ... see below ... },
              "fired_signals": [<driver-rules active on the latest row>],
              "top_drivers": [{"driver": "...", "kind": "symbolic"|"neural",
                               "importance": <0..1 within kind>}, ...],
              "proof_ref": {"proof_checked": bool, "proof_summary": "...",
                            "model_id": ..., "as_of": ...},
              "why_certification": { ... the embedded certificate (verified=True) ... },
              "sector": ..., "period": ..., "entity": ...
            }

        The decision layer reads ``value`` / ``interval`` / ``probability`` /
        ``fired_signals``; ``top_drivers`` is the provenance/why narrative.
        ``proof_ref`` / ``why_certification`` are the proof chain (``why_certification``
        is only populated with ``verified=True``).

        Certified probability (``probability`` / ``probability_basis``)
        --------------------------------------------------------------
        ``probability`` is a CERTIFIED, calibrated probability of the forecast's
        directional outcome — ``P(outcome on the forecast's side of a threshold)``.
        It is derived by the ``gaussian_interval_conformal`` method: the forecast
        interval is read as ``value ± interval_z·sigma`` where ``sigma`` is the
        model's MEASURED out-of-sample error (backtest RMSE etc.), recovered as
        ``sigma = half_width / interval_z`` (no re-fit, no new data), then the
        outcome is modelled ``N(value, sigma)`` and the probability read off. It is
        a monotone map of the model's own signal-to-noise, NOT an independent
        confidence. ``probability_basis`` records how it was derived + whether it is
        certified::

            {"method": "gaussian_interval_conformal",
             "interval_basis": "backtest_rmse",   # the measured-error basis used
             "interval_z": 1.0,                    # z used to build the interval
             "direction": "up"|"down",             # which side of threshold
             "sigma": <recovered out-of-sample sigma>,
             "threshold": <the threshold, default the persistence baseline>,
             "reason": "certified: in_domain and calibration in-regime"}

        ``probability_certified`` — and the FAIL-CLOSED / OOD contract. The
        probability is only valid (``probability_certified=True``, ``probability``
        a number) when BOTH gates pass: (1) the forecast's input row is IN-DOMAIN
        (its ``why_certification`` proof-checked — so this is only certifiable with
        ``verified=True``), and (2) the calibration is in its validated regime — the
        ``interval_basis`` is a REAL measured out-of-sample error basis (one of
        ``driver_bands`` / ``backtest_rmse`` / ``persistence_rmse`` /
        ``target_change_sd``, not a degenerate flat-series floor) and the recovered
        ``sigma`` is finite and positive. If EITHER gate fails — out-of-domain input,
        an out-of-regime interval basis, or a degenerate/non-positive sigma — the
        platform FAILS CLOSED: ``probability`` is ``None`` and
        ``probability_certified`` is ``False``, NEVER a spurious confident number.
        ``probability_basis.reason`` says which gate failed (e.g.
        ``"out_of_domain: why_certification not proof_checked"`` or
        ``"calibration_out_of_regime: ..."``). A downstream decision reading an
        uncertified probability fails closed.

        Addressing the record (naming handles) — and its CONSUMERS
        ----------------------------------------------------------
        The emitted ``prediction_record`` is PERSISTED server-side (org+owner-scoped)
        on every call, so a downstream VERIFIED decision can reference it BY
        (``model_id``, ``as_of``) and the platform folds its certified fields in —
        the caller never re-supplies the value. The CONSUMING methods are
        ``platforms.query(predictions={role: {"model_id": ..., "as_of": ...}})``
        (a verified query/decision) and
        ``agent_policy.authorize_action(predictions={role: {...}})`` (the Agent
        Policy Gate). Reference it with ``verified=True`` so ``proof_ref.proof_checked``
        is True — an unverified / out-of-domain forecast persists NOT-certified and a
        consumer's fail-closed gate then admits no fact (the decision abstains).

        The optional keyword args address/name the emitted ``prediction_record`` so a
        Prediction→Decision consumer can fan several models in by role at a shared
        period. All are additive — omit them and the record still assembles:

        * ``prediction_name`` — semantic role handle (e.g. ``"ust_10y"``); the
          record's ``name``. Defaults to the config's ``target_field``.
        * ``prediction_model_id`` — stable id for the record (``model_id``); defaults
          to ``prediction_name`` / ``target_field``. Used with ``as_of`` as the
          persisted-record key.
        * ``as_of`` — the forecast period; the ALIGNMENT KEY a consuming decision
          shares. Free-form label (e.g. an ISO date ``"2026-06-30"`` or a period tag).
        * ``sector`` / ``period`` / ``entity`` — optional join keys on the record.
        * ``top_drivers_n`` — how many ranked drivers to surface in ``top_drivers``
          (default 5).

        The certification payload is COMPACT BY DEFAULT as of 0.19.0 (the
        breaking flip announced in 0.18.0). The top-level ``why_certification``
        per-feature ``certified_facts`` list (one certificate per engineered
        feature — large on a wide panel) is replaced by a compact
        ``certification_summary`` (``proof_checked`` + counts + min confidence);
        ``proof_checked`` / ``proof_summary`` are retained. To get the FULL proof
        back, pass ``compact_certification=False`` — that restores the full
        ``certified_facts`` list at the top level. The embedded
        ``prediction_record.why_certification`` ALWAYS carries the compact handle
        (it is a proof-carrying handle re-checked by the decision layer, never a
        second copy of the fact list) regardless of the flag.

        **Org-capability gating.** Requires the ``predictions`` capability.
        Returns 403 ``capability_disabled`` when disabled for the org (see
        ``GET /api/v1/capabilities``).
        """
        body: dict[str, Any] = {
            "prediction_config_id": prediction_config_id,
            "verified": verified,
            "include_fitted_series": include_fitted_series,
            "compact_certification": compact_certification,
        }
        if feature_overrides is not None:
            body["feature_overrides"] = feature_overrides
        # Addressing handles — thread a semantic name/role + the as_of
        # alignment key + join keys into the emitted prediction_record. All
        # optional / back-compatible; omit and the record still assembles (name
        # defaults to the config's target_field, as_of to None).
        if prediction_name is not None:
            body["prediction_name"] = prediction_name
        if prediction_model_id is not None:
            body["prediction_model_id"] = prediction_model_id
        if as_of is not None:
            body["as_of"] = as_of
        if sector is not None:
            body["sector"] = sector
        if period is not None:
            body["period"] = period
        if entity is not None:
            body["entity"] = entity
        if top_drivers_n is not None:
            body["top_drivers_n"] = top_drivers_n
        return self._request(
            "POST", f"/api/v1/platforms/{platform_id}/symbolic-forecast", json=body)

    def residual_diagnosis(self, platform_id: int, *, prediction_config_id: int,
                           forecast_id: int | None = None,
                           value: float | None = None,
                           actual: float | None = None,
                           k: float | None = None) -> ResidualDiagnosis:
        """Diagnose a forecast residual — drift vs correction.

        Computes ``residual = actual - value``, standardises it, and when the
        breach gate ``|z| > k`` (default k=2.0) trips, attributes the miss to the
        driver-rules that lost sensitivity: a decayed driver that pointed away
        from the realised move => **drift** (residual likely to keep widening);
        the still-reliable drivers point counter to the move => **correction**
        (target dislocated; residual likely to tighten). Supply EITHER a stored
        ``forecast_id`` (value + backfilled actual read off the record) OR an
        explicit ``value`` + ``actual`` pair. Returns ``{"residual", "z",
        "breached", "diagnosis", "decayed_drivers", "stable_drivers",
        "evidence", ...}`` — a hypothesis surfaced with its evidence.
        """
        body: dict[str, Any] = {"prediction_config_id": prediction_config_id}
        if forecast_id is not None:
            body["forecast_id"] = forecast_id
        if value is not None:
            body["value"] = value
        if actual is not None:
            body["actual"] = actual
        if k is not None:
            body["k"] = k
        return self._request(
            "POST", f"/api/v1/platforms/{platform_id}/residual-diagnosis", json=body)


class ApiKeyResource(_Resource):
    """Manage API keys — create, list, revoke, and zero-downtime **rotate**.

    Keys optionally carry an **expiry** (`expires_at`, ISO-8601; naive values
    are treated as UTC; must be in the future) and can be **rotated** ahead of
    expiry via :meth:`rotate`, which mints a replacement and puts the old key
    into a bounded **grace** window so callers can cut over without downtime.
    Listings surface `expires_at`, `grace_until`, and `rotated_from_id`.
    """

    def list(self) -> list[dict]:
        """List API keys visible to the caller (includes `expires_at`,
        `grace_until`, `rotated_from_id` for rotation/expiry lineage)."""
        return self._request("GET", "/api/v1/api-keys")

    def create(self, *, scope: str = "platform", platform_id: int | None = None,
               name: str = "Default", expires_at: str | None = None) -> dict:
        """Create an API key. The plaintext key is returned exactly once.

        ``expires_at``: optional ISO-8601 datetime after which the key stops
        validating (naive values are treated as UTC; must be in the future,
        else the server returns 422).
        """
        body: dict[str, Any] = {"scope": scope, "name": name}
        if platform_id is not None:
            body["platform_id"] = platform_id
        if expires_at is not None:
            body["expires_at"] = expires_at
        return self._request("POST", "/api/v1/api-keys", json=body)

    def revoke(self, key_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/api-keys/{key_id}")

    def rotate(self, key_id: int, *, grace_seconds: int | None = None,
               expires_at: str | None = None) -> dict:
        """Rotate an API key with zero downtime: mint a replacement and put the
        old key into a bounded **grace** window (default 300s, max 86400s /
        24h; `grace_seconds=0` = immediate cut-over) after which it stops
        validating like a revoked key. The replacement inherits the old key's
        org, owner, platform binding, scope, name, rate limit, token budget,
        IP allowlist, and expiry (override the new key's expiry via
        ``expires_at``). Returns 201 with the new key secret exactly once,
        under ``key``, plus ``rotated_from_id`` and ``old_key`` (its id +
        `grace_until`). Raises on 409 if the key is already revoked, expired,
        or already rotated — create a new key instead.
        """
        body: dict[str, Any] = {}
        if grace_seconds is not None:
            body["grace_seconds"] = grace_seconds
        if expires_at is not None:
            body["expires_at"] = expires_at
        return self._request("POST", f"/api/v1/api-keys/{key_id}/rotate", json=body)


class ConnectorResource(_Resource):
    """Data-source connectors for external economic and financial data.

    Available connectors (call ``list()`` for the full catalogue):

    * **Market data (keyless):** ``yahoo`` (stocks/ETFs), ``coinbase`` (crypto).
    * **Central banks (keyless):** ``boe`` (BoE gilt yields, SONIA), ``ecb``
      (ECB euro-area yield curves).
    * **Government/statistical (keyless):** ``eurostat`` (EU SDMX macro/prices),
      ``fiscaldata`` (US Treasury debt/rates/FX), ``edgar`` (SEC XBRL company
      fundamentals), ``worldbank`` (World Bank development indicators),
      ``oecd`` (OECD SDMX macro).
    * **BYO-key:** ``fred`` / ``fred_sentiment`` (free FRED key -- also supports
      ALFRED point-in-time vintage via ``as_of_date`` / ``vintage``), ``imf``
      (IMF iData SDMX, ``Ocp-Apim-Subscription-Key``).
    * **Other:** ``rest`` (generic REST/CSV, BYO auth via headers), ``gdelt``
      (news tone), ``sentiment`` (LLM-scored RSS sentiment).

    Connectors that hit a credentialed provider require *your own* key, passed in
    the ``config`` dict -- Ambertrace does not supply third-party keys on your
    behalf.

    **Search** (``search()``): resolve natural-language data requests to concrete
    connector and series entries.  Supports structured filters (``asset_class``,
    ``country``, ``region``, ``currency``, ``tenor``) and free-text search.
    Region groups (``asia``, ``europe``, ``developed-markets``, ``G7``, etc.)
    expand to country sets.  A connector tagged ``country='global'`` matches
    every region (e.g. Yahoo Finance under ``region='asia'``).
    """

    def list(self) -> list[dict]:
        """List available connectors and their config requirements."""
        return self._request("GET", "/api/v1/connectors")

    def test(self, *, connector_type: str, config: dict) -> dict:
        """Validate a connector config by fetching a small sample.

        ``config`` carries any provider credentials the connector needs
        (e.g. ``{"api_key": "<your FRED key>", ...}``).
        """
        return self._request(
            "POST",
            "/api/v1/connectors/test",
            json={"connector_type": connector_type, "config": config},
        )

    def search(
        self,
        *,
        q: str | None = None,
        asset_class: str | None = None,
        country: str | None = None,
        region: str | None = None,
        currency: str | None = None,
        tenor: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> dict:
        """Search connectors and series by structured filters and/or free text.

        Resolves natural-language data requests (e.g. ``'5y german rate'``,
        ``'asian equities'``, ``'developed-market FX'``) to concrete connector
        and series entries suitable for building a model.

        All filters are AND-ed.  Results include both **connector-level**
        entries (all registered connectors) and **series-level** entries
        (statically-enumerable series — ECB yield-curve keys, BoE known series,
        FRED DGS rates and common macro indicators).  Series search covers
        the statically-enumerable set; dynamic dataflow enumeration (arbitrary
        FRED/Yahoo/SDMX series) is follow-up.

        Parameters
        ----------
        q : str, optional
            Free-text search term — lexical, case-insensitive substring match
            on connector/series names and descriptions.
        asset_class : str, optional
            Filter by asset class (e.g. ``'rates'``, ``'fx'``,
            ``'economics/macro'``, ``'equities'``, ``'crypto'``).
        country : str, optional
            Filter by country tag (ISO-3166 alpha-2 or aggregate code like
            ``'EA'`` for euro area).  Note: euro-area sovereign yield curves
            are tagged ``country='EA'``, not ``'DE'`` — for German rates, use
            ``region='eurozone'`` instead of ``country='DE'``.
        region : str, optional
            Filter by named region group.  Expands to the constituent country
            codes before filtering.  Available groups: ``'asia'``,
            ``'europe'``, ``'americas'``, ``'developed-markets'``,
            ``'emerging-markets'``, ``'G7'``, ``'G10'``, ``'eurozone'``.
            A connector tagged ``country='global'`` matches every region
            (e.g. Yahoo Finance under ``region='asia'``).
        currency : str, optional
            Filter by currency tag (ISO-4217 alpha-3, e.g. ``'EUR'``,
            ``'USD'``, ``'GBP'``).  Connectors tagged ``'multi'`` match any
            currency filter.
        tenor : str, optional
            Filter by instrument tenor (e.g. ``'5Y'``, ``'10Y'``, ``'3M'``).
            Series-level only — connector-level entries have no tenor.
        offset : int
            Pagination offset (default 0).
        limit : int
            Pagination page size (default 50, max 200).

        Returns
        -------
        dict
            ``{"data": [...], "pagination": {"total": N, "limit": L, "offset": O}}``
            where each item has ``level``, ``connector_type``, ``name``,
            ``description``, ``asset_classes``, ``countries``, ``currencies``,
            and optionally ``tenor``.

        Example — resolving ``'5y german rate'``::

            results = api.connectors.search(
                asset_class="rates", region="eurozone", tenor="5Y",
            )
            for item in results["data"]:
                print(item["name"], item.get("tenor"))
        """
        params: dict[str, str | int] = {}
        if q is not None:
            params["q"] = q
        if asset_class is not None:
            params["asset_class"] = asset_class
        if country is not None:
            params["country"] = country
        if region is not None:
            params["region"] = region
        if currency is not None:
            params["currency"] = currency
        if tenor is not None:
            params["tenor"] = tenor
        if offset:
            params["offset"] = offset
        if limit != 50:
            params["limit"] = limit
        return self._request("GET", "/api/v1/data/search", params=params)


class AgentPolicyResource(_Resource):
    """Author a governance policy in plain English, then PROVE every agent
    action permit/deny against it.

    This is the **Agent Policy Gate**: you write the rules an AI agent must obey
    in natural language; Ambertrace compiles them to a verified policy and proves
    each proposed tool-call permit/deny — fail-closed, with a machine-checked
    proof. The compiled form is internal; you only ever author *English* and read
    back the admitted rules (also rendered in English) plus a permit/deny verdict
    with its proof.

    Typical flow::

        # 1. Author the policy (English in)
        result = api.agent_policy.author(
            "The agent may place orders against an open_positions ledger that "
            "has a quantity column and a price column. The cumulative exposure - "
            "the sum of quantity times price across every row - must stay at or "
            "below 100000. Permit an order only when that cumulative exposure "
            "stays within the limit."
        )
        platform_id = result["platform"]["id"]
        # result["admitted"]  -> the rules that were admitted (plain English)
        # result["rejected"]  -> any proposals that fell outside the verified
        #                        fragment, each with a reason (nothing is silently
        #                        dropped)

        # 2. See exactly which facts an action must supply
        status = api.agent_policy.status()
        status["input_fields"]   # the declared inputs (name/type/range)

        # 3. Gate a single proposed action - permit/deny WITH PROOF
        verdict = api.agent_policy.authorize_action(
            platform_id,
            tool="place_order",
            args={"qty": 100, "price": 400},
        )
        verdict["decision"]       # "permit" | "deny" | a policy's own verb
        verdict["proof_checked"]  # True - the verified engine certified the firing set
        verdict["denied_reason"]  # on a deny, the specific requirement that failed
        verdict["outcome"]        # "permit" | "deny" | "indeterminate" | "unavailable"

    Branch on ``verdict["outcome"]`` - it splits apart THREE different non-permits
    that ``decision``/``permitted`` alone conflate:

    * ``permit`` - within policy; ``permitted`` True, ``proof_checked`` True. Execute.
    * ``deny`` - a PROVEN policy violation; ``permitted`` False, ``proof_checked``
      True. Do not execute, and do NOT blindly retry - the action breaks a rule.
    * ``indeterminate`` - the decision chain needed a declared input it was not
      given, so the gate reached NO verdict. ``permitted`` False, ``proof_checked``
      False. This is NOT a denial (don't give up) and NOT a permit (don't execute):
      the remedy is to supply ``verdict["missing_inputs"]`` and retry.
    * ``unavailable`` - the verified engine could not run (e.g. checker disabled).
      ``permitted`` False, ``proof_checked`` False - again, no verdict was reached.

    For a CUMULATIVE control (a running count / sum / exposure over a history of
    prior actions) OR a TEMPORAL / sequencing control (precedence, bounded-window
    rate, request/response pairing over the ORDERED history), open a *session*
    instead of gating one action: the harness is the sole executor and accumulates
    the ordered executed-action ledger, so the gate can prove the obligation over
    the *resulting* history (see :meth:`create_session` / :meth:`step`).

    -- Supported obligation classes (what you can express in English) ----------

    Every policy is a set of requirements an action must satisfy. Each requirement
    is one of these classes; you express it in plain English and the compiler
    admits it as a verified obligation. (Anything outside these classes is
    rejected-and-surfaced in ``result["rejected"]`` - never silently approximated.)

    1. **Per-action condition** - a check on the proposed action's own fields.
       *English:* "Only allow actions of type triage, schedule, or refer."
       "Block any actuator command with pressure outside 2 to 8 bar." "Require
       mfa_passed for privileged requests."

    2. **Cumulative count / sum limit** - a cap on a running ``count`` or ``sum``
       over a declared ledger of prior actions. Name the ledger and the column;
       only ``count`` and ``sum`` are supported (never average/min/max).
       *English (sum):* "Each order writes a row to an order_log with a quantity
       column. The total quantity summed across all rows must stay at or below
       1000." *English (count):* "No more than 3 actions of this kind may be
       executed."

    3. **Cumulative exposure** ``sum of qty x price <= limit`` - a cap on the
       running *value* (the sum of a quantity column times a price column) over a
       declared ledger. The limit must be a numeric constant.
       *English:* "Each order writes a row to an open_positions ledger with a
       quantity column and a price column. The cumulative exposure - the sum of
       quantity times price across every row - must stay at or below 100000."

    4. **Interval / band binding** - an exposure cap that must hold for *every*
       value of ONE as-yet-unknown factor confined to a closed interval
       ``[lo, hi]`` (e.g. a fill price not yet known but guaranteed to fall in a
       band). The bound is proven for ALL values in the band, not just a sample.
       *English:* "For a proposed order whose fill price is not yet known but is
       guaranteed to be between 100 and 500, the cumulative exposure must stay at
       or below 100000 for every possible fill price in that range."

    5. **Temporal / sequencing** - an ORDER-carrying obligation over the session's
       ordered ledger of prior EXECUTED actions. Three decidable folds are
       supported:

       * **Precedence** (``precededBy``) - an action must be PRECEDED BY an earlier
         action on the same key. *English:* "Permit a deploy for a service only
         when it is preceded by an approval for the same service in the same
         session." (trigger idioms: "preceded by" / "before" / "prior to")
       * **Bounded window / rate** (``boundedWindow``) - at most N matching actions
         on a key within any sliding window of W of that key's actions. *English:*
         "No more than 3 deploys to a service within any 5 of that service's
         actions."
       * **Request/response pairing** (``noUnmatchedResponse``) - every response on
         a key must be matched by a DISTINCT earlier request. *English:* "Every
         reply must be paired with an earlier distinct request in the same session."

       Temporal obligations fold over the ACCUMULATED ORDERED LEDGER, so they need a
       :meth:`create_session` + :meth:`step` loop (the ledger records only executed
       actions in order) - a single :meth:`authorize_action` gates an EMPTY ledger,
       so e.g. the first deploy has nothing to be preceded by and is denied. The
       antecedent action (e.g. the approval) must itself reach a permit under the
       policy or it never enters the ledger. See example 40.

    6. **Distinct-actor quorum** (``distinct_count``) - at least N DIFFERENT actors
       must appear across a per-request set of prior sign-offs. The kernel computes
       the distinct count over CERTIFIED rows - a caller cannot self-attest a count,
       and two sign-offs from the same actor fold to one. *English:* "Permit a
       production deploy only when at least two DIFFERENT approvers have signed off."
       Supply the sign-offs via :meth:`authorize_action`'s ``relations`` (the
       per-request set), e.g. ``relations={"approvals": [{"approver_id": "bob"},
       {"approver_id": "carol"}]}``.

    7. **Separation of duties** (cross-field inequality / ``not_member``) - two
       named fields must differ, or an actor must not be a member of a set.
       *English:* "The approver must not be the author." Enforced INLINE by the
       kernel with no discharge fact. See example 28 (``approver`` != ``author``).

    Author the requirement in English, then ALWAYS confirm it admitted as you
    intended by reading ``result["admitted"]`` (the rules in plain English) and
    ``result["rejected"]`` (anything that fell outside the verified fragment) -
    and by running a within-limit action (expect permit) and a breaching action
    (expect deny) through the gate before relying on the policy. The intent
    safeguard is review + test, not a fixed vocabulary.

    -- Availability ------------------------------------------------------------

    The Agent Policy Gate is a preview capability. Its endpoints are flagged and
    return :class:`AmbertraceError` (404) when the gate is not enabled on the
    deployment you are hitting. The cumulative / exposure / band classes
    additionally require the platform's numeric obligation checker to be enabled.
    """

    def author(self, policy_text: str, *, timeout: float = 300.0,
               poll_interval: float = 3.0) -> AuthorResult:
        """Compile an English governance policy into a verified policy and
        build/replace the org's agent-policy gate.

        ``policy_text`` is the rules an agent must obey, in natural language (see
        the class docstring for the supported obligation classes + example
        phrasings). Returns ``{"platform": {...}, "admitted": [{"name",
        "description", "kind"}, ...], "rejected": [{"name", "reason"}, ...],
        "policy_text": ..., "decision_vocabulary"?: {...}}``.

        * ``admitted`` - the rules that were admitted, each described in plain
          English. This is the authoritative read-back of what your policy
          *means*; review it.
        * ``rejected`` - every proposal that fell outside the verified fragment,
          with a reason. Nothing is silently dropped: a requirement you expected
          and do not see in ``admitted`` will appear here with why it was rejected.

        An empty or vacuous policy fails closed: the call raises
        :class:`AmbertraceError` (422) and the existing policy (if any) is left
        unchanged.

        **Ownership / authority.** The org has ONE agent-policy gate. The FIRST
        ``author`` call creates it and makes the calling user its owner. Once a
        gate EXISTS, only its **owner** or an **org-admin** may replace it —
        authoring as anyone else raises :class:`AmbertraceError` (**404
        ``not_found``**). The 404 is intentional governance scoping (it is
        deliberately a 404, not a 403, so the gate's existence is not revealed to
        an unauthorised caller) — it does NOT mean authoring is unavailable. So a
        404 from ``author`` means EITHER (a) the agent-policy-gate feature is not
        enabled on your deployment, OR (b) an org gate already exists and your
        credentials lack write authority over it. To replace an existing org
        gate, author with the gate owner's credentials or an org-admin key; a
        platform-scoped key bound to a different platform cannot replace it.

        **Blocking.** Server-side, authoring is asynchronous: the POST returns a
        ``{"job_id", "status": "processing"}`` ticket and the compile+build runs in
        the background. This method hides that — it polls the job to completion and
        returns the compiled ``{"platform", "admitted", "rejected", ...}`` result, so
        the documented synchronous contract holds. ``timeout`` (seconds) bounds the
        wait (raising :class:`TimeoutError` if the build runs long); ``poll_interval``
        is the gap between status checks. A ``vacuous`` policy raises
        :class:`AmbertraceError` (422); a transient compiler outage raises
        :class:`AmbertraceError` (503). (A deployment that still answers the POST
        synchronously is passed straight through.)
        """
        started = self._request(
            "POST", "/api/v1/agent-policy-gate/policy",
            json={"policy_text": policy_text})
        # Back-compat: a deployment that compiles synchronously returns the built
        # gate inline (``platform`` present / ``status == "done"``) — pass it through.
        if (not isinstance(started, dict) or "platform" in started
                or started.get("status") == "done"):
            return cast(AuthorResult, started)
        job_id = started.get("job_id")
        if not job_id:
            return cast(AuthorResult, started)  # unrecognised shape — return as-is rather than hang
        # Async: poll the compile job to a terminal status.
        deadline = time.monotonic() + timeout
        while True:
            job = self._request(
                "GET", f"/api/v1/agent-policy-gate/policy/jobs/{job_id}")
            status = job.get("status", "") if isinstance(job, dict) else ""
            if status == "done":
                return cast(AuthorResult, job)
            if status in ("vacuous", "unavailable", "error"):
                raise AmbertraceError(
                    422 if status == "vacuous" else 503,
                    f"author_{status}",
                    (job.get("message")
                     or f"Policy authoring did not complete ({status})."),
                )
            if time.monotonic() >= deadline:
                raise TimeoutError(
                    f"author did not complete within {timeout:.0f}s "
                    f"(job {job_id}, last status: {status or 'unknown'})")
            time.sleep(poll_interval)

    def status(self) -> AgentPolicyStatus:
        """The org's live agent-policy gate: the active policy text, the admitted
        controls (plain English), and the DECLARED INPUT fields an action must
        supply.

        Returns ``{"enabled": True, "platform": {...}|None, "policy_text": ...,
        "admitted_controls": [{"name", "description"}, ...], "input_fields":
        [{"name", "type", "enum_values"?, "min_value"?, "max_value"?,
        "description"?}, ...], "relations": [{"name", "columns": [{"name",
        "type"}], "max_rows"?}, ...], "decision_vocabulary"?: {...}}``.

        ``input_fields`` is the contract for :meth:`authorize_action` / :meth:`step`
        - supply a value for each (under ``args`` or ``context``) so the gate
        returns a real permit/deny rather than rejecting an unknown/missing fact.

        ``relations`` is the contract for :meth:`authorize_action`'s ``relations``
        param - the per-request multi-row SETS a policy reasons over (e.g. the
        approvals backing a distinct-actor quorum). Send ``{<relation name>: [{<col>:
        value}, ...]}`` using the names/columns listed here. Empty for a policy that
        declares no relation.
        """
        return self._request("GET", "/api/v1/agent-policy-gate")

    def examples(self) -> list[dict]:
        """The built-in example-policy library: ``[{"id", "domain_label",
        "title", "policy_text", "try_hint"}, ...]``. Each ``policy_text`` is a
        ready-to-author English policy you can pass straight to :meth:`author`."""
        return self._request("GET", "/api/v1/example-policies")

    def authorize_action(self, platform_id: int, *, tool: str,
                         args: dict | None = None,
                         context: dict | None = None,
                         relations: dict | None = None,
                         predictions: dict[str, dict[str, str | None]] | None = None,
                         ) -> AuthorizeActionResult:
        """Gate ONE proposed tool-call against the verified policy - permit/deny
        WITH PROOF.

        ``args`` are the action's intrinsic fields; ``context`` carries ambient
        facts the policy reasons over (``args`` wins on a key collision). Supply a
        value for each of :meth:`status`'s ``input_fields``.

        ``predictions`` (``{role: {"model_id": str, "as_of": str|None}}``) is the
        native, FAIL-CLOSED Prediction -> Decision fan-in INTO the gate — gate an
        agent action against a VERIFIED forecast this org already produced +
        persisted (via :meth:`PredictionResource.symbolic_forecast`), referenced by
        ``model_id`` + alignment ``as_of``. The gate fetches the org+owner-scoped
        stored ``prediction_record`` and admits ONLY its certified fields to the
        decision's certified EDB keyed ``<role>.<field>`` (``<role>.value``,
        ``<role>.probability`` iff the record's probability certified,
        ``<role>.fired.<signal>``); the caller NEVER supplies the forecast value.
        A policy rule reading ``<role>.value`` / ``<role>.probability`` then gates
        the action over that trusted forecast. FAIL-CLOSED: a reference that is
        missing / not ``proof_checked`` / ``as_of``-mismatched / (for probability)
        not certified admits NO fact, so the rule cannot fire a certified permit and
        the action is DENIED rather than permitted on an uncertified / low-confidence
        forecast. (A forecast is only ``proof_checked`` when produced with a certified
        in-domain input + in-regime calibration, i.e. ``symbolic_forecast(verified=
        True)``.) Verified gate platforms only.

        Example (gate a spend/deploy action against a certified forecast)::

            api.agent_policy.authorize_action(
                pid, tool="place_order", args={"qty": 100},
                predictions={"vol_forecast":
                             {"model_id": "vol_1d", "as_of": "2026-06-30"}})
            # a policy rule reading `vol_forecast.value` decides over the
            # platform-produced, certified forecast — never a caller-asserted number.

        (NOTE: :meth:`step` does NOT accept ``predictions`` — the session ledger
        path is for CUMULATIVE obligations; fan a certified forecast in via this
        single-action method.)

        ``relations`` supplies caller-provided multi-row SETS for a policy that
        reasons over a declared relation as a PER-REQUEST set rather than an
        accumulated ledger — e.g. the approvers backing a distinct-actor quorum
        ("at least two DIFFERENT approvers, none the author")::

            api.agent_policy.authorize_action(
                pid, tool="deploy", args={"environment": "prod", "author": "alice"},
                relations={"approvals": [{"approver_id": "bob"},
                                          {"approver_id": "carol"}]})

        Each row is independently certified (declared column / in-domain / ground)
        and the kernel COMPUTES the aggregate over the certified rows — a caller
        cannot self-attest a count, and two sign-offs from the same actor fold to one
        distinct key. Use a :meth:`create_session` + :meth:`step` loop instead when
        the obligation is CUMULATIVE over actions the agent itself executes.

        Returns ``{"decision", "permitted", "proof_checked", "proof_summary",
        "denied_reason", "deciding_rule"?, "certified_facts", "rejected_facts",
        "outcome", "missing_inputs", "stalled_stage", "query_diagnostics"}``.
        ``decision`` is the policy's verdict verb (``permit``/``deny``, or a custom
        verb the policy declares). Fail-closed: a rejected/missing fact, a
        proof-check failure, or an unavailable engine yields no permit - never a
        default-allow.

        ``outcome`` is the field to BRANCH on - it separates the three distinct
        non-permits that ``decision``/``permitted`` alone hide:

        * ``outcome == "permit"`` - within policy (``permitted`` True,
          ``proof_checked`` True). Execute the action.
        * ``outcome == "deny"`` - a PROVEN policy violation (``permitted`` False,
          ``proof_checked`` True). See ``denied_reason``. Do NOT blindly retry.
        * ``outcome == "indeterminate"`` - the decision chain needed a declared
          input that was not supplied or derived, so the gate reached NO verdict.
          INVARIANT: ``permitted`` is False and ``proof_checked`` is False - this is
          NOT a denial and NOT a permit. The remedy is to supply the field(s) in
          ``missing_inputs`` and retry (don't give up, don't execute).
        * ``outcome == "unavailable"`` - the verified engine could not run (e.g. the
          numeric checker is disabled). Same invariant: ``permitted`` False,
          ``proof_checked`` False; no verdict was reached.

        Supporting diagnostics on a non-permit:

        * ``missing_inputs`` - ``list[str]``: declared input field(s) the decision
          chain needed but did not get. Populated on ``indeterminate``; supply these
          and retry.
        * ``stalled_stage`` - ``str | None``: the decision stage the chain stalled at.
        * ``query_diagnostics`` - ``{"missing_atoms", "deciding_rule",
          "rejected_facts", "stalled_stage"}``: the underlying why-it-stalled detail.

        Detect -> supply -> retry::

            v = api.agent_policy.authorize_action(pid, tool="t", args={...})
            if v["outcome"] == "indeterminate":
                needs = v["missing_inputs"]   # e.g. ["target_zone"] - supply + retry
            elif v["permitted"]:
                ...                            # within policy (proof_checked True)
            else:
                ...                            # proven deny - do not blindly retry

        An ``indeterminate`` outcome is NOT a policy denial (don't give up) and NOT
        a permit (don't execute): it means the gate lacked an input it needed. Fill
        in ``missing_inputs`` (under ``args`` or ``context``) and call again.

        For a CUMULATIVE or TEMPORAL obligation (classes 2-5) this gates the action
        against an EMPTY history - use a :meth:`create_session` + :meth:`step` loop
        so the obligation is proven over the accumulated ordered executed-action
        ledger.
        """
        action: dict = {"tool": tool, "args": args or {}}
        body: dict = {"action": action}
        if context is not None:
            body["context"] = context
        if relations is not None:
            body["relations"] = relations
        if predictions is not None:
            body["predictions"] = predictions
        return self._request(
            "POST", f"/api/v1/platforms/{platform_id}/authorize-action", json=body)

    def create_session(self, *, platform_id: int,
                       goal: str | None = None) -> SessionResult:
        """Open a mediated agent session bound to a verified agent-policy gate.

        Every action proposed via :meth:`step` is gated; the harness is the SOLE
        executor (no bypass) and accumulates the ORDERED executed-action ledger, so a
        CUMULATIVE obligation (count / sum / exposure / band) OR a TEMPORAL /
        sequencing obligation (precedence / bounded-window rate / request-response
        pairing) is proven over the *resulting* ordered history. Returns the session
        (``{"id", "platform_id", "goal", "trace": [...]}``)."""
        body: dict = {"platform_id": platform_id}
        if goal is not None:
            body["goal"] = goal
        return self._request("POST", "/api/v1/agent-sessions", json=body)

    def step(self, session_id: str, *, tool: str, args: dict | None = None,
             context: dict | None = None) -> StepResult:
        """Mediate ONE proposed action in a session: gate -> execute-on-permit /
        block-on-deny.

        The mediation invariant: an effect occurs IFF the gate returned permit
        with a checked proof. On a cumulative policy, the executed action's row
        joins the ledger so the next step's obligation folds over the resulting
        history. Returns ``{"session": {...}, "step": {"verdict": {...},
        "executed": bool, "effect": ...}}``.

        ``step["verdict"]`` carries the SAME shape as :meth:`authorize_action`,
        including the ``outcome`` field (``"permit"`` | ``"deny"`` |
        ``"indeterminate"`` | ``"unavailable"``) plus ``missing_inputs``,
        ``stalled_stage`` and ``query_diagnostics``. Branch on ``outcome``: an
        ``indeterminate`` verdict leaves ``executed`` False and is NOT a denial - the
        gate lacked a declared input (``verdict["missing_inputs"]``); supply it and
        re-issue the step rather than treating it as a policy block. A ``deny`` is a
        proven violation - do not blindly retry."""
        action: dict = {"tool": tool, "args": args or {}}
        body: dict = {"action": action}
        if context is not None:
            body["context"] = context
        return self._request(
            "POST", f"/api/v1/agent-sessions/{session_id}/step", json=body)

    def get_session(self, session_id: str) -> SessionResult:
        """Fetch a session and its full mediated step trace."""
        return self._request("GET", f"/api/v1/agent-sessions/{session_id}")


class JobResource(_Resource):
    def get(self, job_id: int | str) -> JobOut:
        """Fetch a job by id.

        ``job_id`` is typically an ``int``, but some deployments/resources use
        string ids (a session job id polled by ``author``); ``int | str`` is
        accepted and interpolated into the path either way.

        Two job *types* surface through this one endpoint — be sure you are
        polling the right one:

        * **Ontology build** (``type: "ontology"``) — created by
          :meth:`DomainResource.build_ontology`. Its ``result`` is the ontology
          itself, and this job has **no** ``generation_diagnostics``.
        * **Platform build** (``type: "build"``) — the ``build_job`` returned by
          :meth:`PlatformResource.create`. Its ``result.build_quality`` carries
          the customer-facing build-quality summary and its
          ``result.generation_diagnostics`` the underlying decision-coverage
          detail (see :meth:`AmbertraceAPI.wait_for_job`).

        A consumer polling the *ontology* job id will never see
        ``generation_diagnostics``; poll the **platform build job** id instead.
        """
        return self._request("GET", f"/api/v1/jobs/{job_id}")


class UsageResource(_Resource):
    def get(self) -> dict:
        """Return the caller's API usage summary."""
        return self._request("GET", "/api/v1/usage")


class AmbertraceAPI:
    """High-level client for the Ambertrace API.

    Usage:
        api = AmbertraceAPI(base_url="https://app.ambertrace.ai", api_key="at_...")
        domains = api.domains.list()
        platform = api.platforms.create(domain_id=1, dataset_id=2)
        job = api.wait_for_job(platform["job_id"])

    Or read credentials from the environment (``AMBERTRACE_API_KEY`` /
    ``AMBERTRACE_BASE_URL``), with no auth boilerplate::

        api = AmbertraceAPI.from_env()

    ``base_url`` / ``api_key`` are optional on the constructor too: when not
    passed they fall back to those env vars (``base_url`` further defaults to the
    production endpoint ``https://app.ambertrace.ai``). An explicit argument
    always wins over the environment.
    """

    def __init__(self, *, base_url: str | None = None, api_key: str | None = None,
                 timeout: float = 30.0, warm: bool = True):
        base_url = base_url or os.environ.get(_ENV_BASE_URL) or _DEFAULT_BASE_URL
        api_key = api_key or os.environ.get(_ENV_API_KEY)
        if not api_key:
            raise ValueError(
                f"api_key is required: pass api_key=... or set ${_ENV_API_KEY}"
            )
        if _is_wrong_api_host(base_url):
            raise ValueError(
                f"base_url host '{_WRONG_API_HOST}' is not the API endpoint — "
                f"use 'https://{_API_HOST}'."
            )
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )
        # Proactively wake the scale-to-zero machine so it is (or is becoming)
        # ready by the time the caller issues its first real request — the wake
        # then overlaps the caller's setup rather than stalling the first call.
        # Best-effort: never raises. Pass ``warm=False`` to skip (e.g. tests).
        if warm:
            self._ping_health()

    @classmethod
    def from_env(cls, *, dotenv_path: str | None = None, timeout: float = 30.0,
                 warm: bool = True) -> "AmbertraceAPI":
        """Construct a client from the environment — the zero-boilerplate path.

        Reads the API key from ``AMBERTRACE_API_KEY`` and the base URL from
        ``AMBERTRACE_BASE_URL`` (falling back to the production endpoint
        ``https://app.ambertrace.ai`` when unset).

        Pass ``dotenv_path`` to also load a ``.env`` file (e.g.
        ``AmbertraceAPI.from_env(dotenv_path=".env")``); the real process
        environment takes precedence over ``.env`` values, so an exported
        variable always wins. Raises :class:`ValueError` if no API key is found
        in either source.
        """
        file_vals = _load_dotenv(dotenv_path) if dotenv_path else {}
        api_key = os.environ.get(_ENV_API_KEY) or file_vals.get(_ENV_API_KEY)
        base_url = (
            os.environ.get(_ENV_BASE_URL)
            or file_vals.get(_ENV_BASE_URL)
            or _DEFAULT_BASE_URL
        )
        if not api_key:
            src = f"${_ENV_API_KEY}" + (" or the .env file" if dotenv_path else "")
            raise ValueError(f"No API key found: set {src}.")
        return cls(base_url=base_url, api_key=api_key, timeout=timeout, warm=warm)

    def _ping_health(self) -> None:
        """Best-effort ping to the UI health endpoint (the process Fly health-
        checks). Wakes a suspended machine via auto-start and keeps it warm
        during long operations. Never raises."""
        try:
            self._http.get(_HEALTH_PATH, timeout=5.0)
        except Exception:
            pass

    def warm(self) -> None:
        """Proactively wake / keep the platform warm (public, best-effort)."""
        self._ping_health()

    def close(self):
        self._http.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    @property
    def api_keys(self) -> ApiKeyResource:
        return ApiKeyResource(self._http)

    @property
    def domains(self) -> DomainResource:
        return DomainResource(self._http)

    @property
    def datasets(self) -> DatasetResource:
        return DatasetResource(self._http)

    @property
    def platforms(self) -> PlatformResource:
        return PlatformResource(self._http)

    @property
    def predictions(self) -> PredictionResource:
        return PredictionResource(self._http)

    @property
    def connectors(self) -> ConnectorResource:
        return ConnectorResource(self._http)

    @property
    def jobs(self) -> JobResource:
        return JobResource(self._http)

    @property
    def agent_policy(self) -> AgentPolicyResource:
        """Author a governance policy in plain English and prove every agent
        action permit/deny against it (the Agent Policy Gate — preview; see
        :class:`AgentPolicyResource`)."""
        return AgentPolicyResource(self._http)

    @property
    def usage(self) -> UsageResource:
        return UsageResource(self._http)

    def version(self) -> dict:
        """Build identity of the running deployment — ``{version, git_sha,
        built_at}`` — so you can confirm exactly which deploy you are hitting
        (``GET /api/v1/version``; the same fields are also on ``GET
        /api/v1/health``). Sends ``Accept: application/json`` explicitly: without
        it a JSON API path can fall through to the SPA shell (index.html, 200)
        instead of returning JSON."""
        return _Resource(self._http)._request(
            "GET", "/api/v1/version", headers={"Accept": "application/json"})

    def wait_for_job(self, job_id: int | str, *, timeout: int = 600, poll_interval: int = 5,
                     on_progress: Callable[[JobOut], None] | None = None,
                     stall_timeout: float | None = None) -> JobOut:
        """Poll a job until it reaches a terminal status or times out.

        On a terminal FAILED status (``error`` / ``failed``) this **raises**
        :class:`AmbertraceError`, surfacing the job's ``error_message`` — so a
        failed build is no longer swallowed (which would otherwise mislead a
        later ``platforms.query()`` into a "Platform is not active" error). On a
        success status (``ready`` / ``active`` / ``completed``) it returns the
        full job dict as before. A build that completes with
        ``build_quality.status == "needs_review"`` (warnings only) is NOT a
        failure — its status is a success status, so it still returns normally.

        Pass the **platform build job** id (the ``build_job`` returned by
        :meth:`PlatformResource.create`) to get the build-generation
        diagnostics — NOT the ontology build job id (see :meth:`JobResource.get`
        for the two-job distinction).

        **Build quality.** For a platform build, the returned job's
        ``result["build_quality"]`` is the customer-facing structural-health
        summary — the honest, label-free substitute for an accuracy number
        (which can't transfer to your domain)::

            {"status": "ok" | "warnings" | "needs_review",
             "checks": [{"id": str,
                         "severity": "blocking" | "warning" | "info",
                         "ok": bool, "detail": str, "items": [str, ...]}, ...]}

        ``status`` is ``needs_review`` whenever any *blocking* check fails — the
        platform cannot reach a declared decision class, or
        it has no restrictive (deny / block) decision and so permits everything.
        The same block is persisted on the platform and readable later via
        :meth:`PlatformResource.build_quality` / :meth:`PlatformResource.blocking_checks`.

        **Build-generation diagnostics.** For a platform build, the returned
        job's ``result["generation_diagnostics"]`` is the underlying detail
        behind ``build_quality`` — it reports what rule generation produced and
        how the rule set behaves. It is the fastest way to explain why a built
        platform reaches (or never reaches) an adverse decision. Fields:

        * ``rule_count``, ``classifier_count``, ``verdict_conclusion_count``,
          ``connected_restrictive_count`` (ints) — counts of generated rules,
          classifier rules, deny/block conclusion rules, and restrictive rules
          actually wired into a conclusion.
        * ``can_decide_adversely`` (bool) — ``False`` means the rule set
          classifies inputs but has no deny/block conclusion, so the platform
          *permits everything* and can never refuse.
        * ``decision_coverage_warnings`` (list[str]) — human-readable reasons the
          rule set may under-decide (e.g. a missing deny path).
        * ``non_discriminating_rules`` (list[str]) — rules that fire on every
          input (carry no discriminating signal).
        * ``unbound_references`` (list) — references to atoms/predicates that are
          never defined.
        * ``orphan_derived`` (list[str]) — derived atoms that no conclusion
          consumes.

        Interpreting it: ``verdict_conclusion_count == 0`` (equivalently
        ``can_decide_adversely is False``) means the platform reached no
        deny/block decision; ``decision_coverage_warnings`` explains why.

        **Progress + stall detection** (feature-sdk-dx item 6; both optional and
        back-compatible — the existing two-arg signature is unchanged):

        * ``on_progress`` — a callback invoked with the full job dict after every
          poll (terminal poll included). Use it to surface live progress, e.g.
          ``on_progress=lambda j: print(j.get("status"), j.get("progress"))``.
          Exceptions raised by the callback propagate to the caller.
        * ``stall_timeout`` — if set, raise :class:`TimeoutError` when the job
          makes **no forward progress** for this many seconds, even though the
          overall ``timeout`` has not elapsed. "Forward progress" is a change in
          either ``status`` or ``progress`` between polls. This catches a build
          that hangs (e.g. stuck at ``building_ontology`` progress ``0``) without
          waiting out the full ``timeout`` — so a caller can detect a hang and
          delete-and-recreate rather than hand-rolling a ``build_resilient``
          retry wrapper.
        """
        deadline = time.monotonic() + timeout
        last_progress_marker: Any = _UNSET
        last_progress_at = time.monotonic()
        while True:
            job = self.jobs.get(job_id)
            status = job.get("status", "")
            if on_progress is not None:
                on_progress(job)

            # Stall detection: a change in status OR progress counts as forward
            # progress and resets the stall clock.
            marker = (status, job.get("progress"))
            now = time.monotonic()
            if marker != last_progress_marker:
                last_progress_marker = marker
                last_progress_at = now

            if status in ("ready", "active", "error", "failed", "completed"):
                if status in ("error", "failed"):
                    raise AmbertraceError(
                        500, "job_failed",
                        f"Job {job_id} failed (job {job_id}: "
                        f"{job.get('error_message') or status})",
                    )
                return job
            if now >= deadline:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s (last status: {status})")
            if stall_timeout is not None and (now - last_progress_at) >= stall_timeout:
                raise TimeoutError(
                    f"Job {job_id} stalled — no forward progress for "
                    f"{stall_timeout:.0f}s (last status: {status}, "
                    f"progress: {job.get('progress')})"
                )
            # Keep the UI process (the health-gated one) warm alongside the API
            # status polls, so a long build doesn't let the machine suspend
            # mid-job. Best-effort.
            self._ping_health()
            time.sleep(poll_interval)
