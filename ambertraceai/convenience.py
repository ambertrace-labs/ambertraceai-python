"""AmbertraceAI Python SDK — convenience layer over the generated client."""

from __future__ import annotations

import os
import random
import time
import urllib.parse
from typing import Any, Callable

import httpx

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

        Prefers an explicit ``rejected_facts`` list off the error body (the
        structured fail-closed query error — item 3); falls back to the
        ``field`` names carried in ``details`` for back-compatibility.
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
    def list(self) -> list[dict]:
        return self._request("GET", "/api/v1/domains")

    def create(self, *, name: str, description: str, **kwargs) -> dict:
        return self._request("POST", "/api/v1/domains", json={"name": name, "description": description, **kwargs})

    def get(self, domain_id: int) -> dict:
        return self._request("GET", f"/api/v1/domains/{domain_id}")

    def update(self, domain_id: int, **kwargs) -> dict:
        return self._request("PUT", f"/api/v1/domains/{domain_id}", json=kwargs)

    def delete(self, domain_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/domains/{domain_id}")

    def build_ontology(self, domain_id: int) -> dict:
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
        """
        return _normalise_envelope(
            self._request("POST", f"/api/v1/domains/{domain_id}/build-ontology"))

    # -- Evaluation config --

    def eval_config(self, domain_id: int) -> dict:
        return self._request("GET", f"/api/v1/domains/{domain_id}/eval-config")

    def set_eval_config(self, domain_id: int, **kwargs) -> dict:
        return self._request("PUT", f"/api/v1/domains/{domain_id}/eval-config", json=kwargs)

    def delete_eval_config(self, domain_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/domains/{domain_id}/eval-config")

    def suggest_eval_config(self, domain_id: int) -> dict:
        return self._request("POST", f"/api/v1/domains/{domain_id}/eval-config/suggest")

    # -- Rule templates --

    def list_templates(self, domain_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/domains/{domain_id}/templates")

    def create_template(self, domain_id: int, **kwargs) -> dict:
        return self._request("POST", f"/api/v1/domains/{domain_id}/templates", json=kwargs)

    def update_template(self, domain_id: int, template_id: int, **kwargs) -> dict:
        return self._request("PUT", f"/api/v1/domains/{domain_id}/templates/{template_id}", json=kwargs)

    def delete_template(self, domain_id: int, template_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/domains/{domain_id}/templates/{template_id}")

    def feedback_stats(self, domain_id: int) -> dict:
        return self._request("GET", f"/api/v1/domains/{domain_id}/feedback-stats")


class DatasetResource(_Resource):
    def list(self) -> list[AttrDict]:
        """List the caller's datasets.

        Each item is an :class:`AttrDict` — subscriptable as before
        (``ds["row_count"]``) and attribute-accessible (``ds.row_count``,
        ``ds.column_count``, ``ds.decision_column``) for IDE autocomplete.
        """
        return [_wrap(d) for d in self._request("GET", "/api/v1/datasets")]

    def get(self, dataset_id: int) -> AttrDict:
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
               decision_column: str | None = None) -> AttrDict:
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

    def fetch(self, *, domain_id: int, connector_type: str, config: dict | None = None) -> dict:
        """Ingest a dataset from a registered connector (e.g. 'fred', 'yahoo',
        'coinbase', 'rest'). ``config`` carries connector-specific options and any
        bring-your-own-key credentials (e.g. {'api_key': ...} for FRED). See
        api.connectors.list() for available connectors and their requirements.
        """
        body: dict[str, Any] = {
            "domain_id": domain_id,
            "connector_type": connector_type,
            "config": config or {},
        }
        return self._request("POST", "/api/v1/datasets/fetch", json=body)

    def fetch_multi(self, *, domain_id: int, sources: list[dict],
                    join_on: str = "date", frequency: str | None = None,
                    aggregation: str | None = None) -> dict:
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

    def clean(self, dataset_id: int, *, steps: list[str] | None = None) -> dict:
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
    def list(self) -> list[dict]:
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
        """
        body: dict[str, Any] = {"domain_id": domain_id, "dataset_id": dataset_id, **kwargs}
        if name:
            body["name"] = name
        return _normalise_envelope(self._request("POST", "/api/v1/platforms", json=body))

    def get(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}")

    def build_quality(self, platform_id: int) -> dict | None:
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

    def blocking_checks(self, platform_id: int) -> list[dict]:
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

    def status(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/status")

    def query(self, platform_id: int, *, query: str, explain: bool = True, **kwargs) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/query", json={"query": query, "explain": explain, **kwargs})

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
                feature_overrides: dict | None = None, explain: bool = True) -> dict:
        """Run a prediction with a trained config.

        ``feature_overrides`` is an optional dict of what-if feature values
        (e.g. {"inflation": 5.0}); omit it to predict from the latest data. For
        timeseries configs a raw-column override is injected into the most-recent
        point and the engineered features the model consumes (lags / rolling /
        rate-of-change) are recomputed from it, so the forecast actually moves.
        Any override key that maps to no model-consumed feature is returned in
        the response's ``unmatched_overrides`` list (and ignored), so a what-if
        that could not be applied is visible rather than a silent no-op.
        """
        body: dict[str, Any] = {"prediction_config_id": prediction_config_id, "explain": explain}
        if feature_overrides is not None:
            body["feature_overrides"] = feature_overrides
        return self._request("POST", f"/api/v1/platforms/{platform_id}/predict", json=body)

    def list_configs(self, platform_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/prediction-configs")

    def create_config(self, platform_id: int, **kwargs) -> dict:
        """Create a prediction config on a platform.

        Pass any of the config fields as keyword args, e.g. ``target_field``,
        ``time_index_field``, ``horizon``, ``frequency``, ``model_type``,
        ``feature_fields``, ``feature_config``.

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

        Metrics (see :meth:`PlatformResource.prediction_model` /
        ``predict(...)["explanation"]["model"]["metrics"]``): when a
        ``target_transform`` (difference / pct-change / log-diff) is applied, the
        ``metrics`` block reports THREE views so no single number misleads:
        ``transformed`` ({r2, rmse, mae} on the modelled change — the hard part),
        ``level`` ({r2, rmse, mae} on the reconstructed level — what you track,
        rebuilt from the realized previous level for a 1-step backtest), and
        ``skill_vs_persistence`` (level-space — the part the model adds over
        predicting last value), plus ``target_transform``. With no transform,
        ``transformed == level`` (backward compatible).
        """
        return self._request("POST", f"/api/v1/platforms/{platform_id}/prediction-configs", json=kwargs)

    def delete_config(self, platform_id: int, config_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/platforms/{platform_id}/prediction-configs/{config_id}")

    def train(self, platform_id: int, config_id: int) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/prediction-configs/{config_id}/train")

    def list_predictions(self, platform_id: int) -> list[dict]:
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
                   poll_interval: float) -> dict:
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
                                  poll_interval: float = 5.0) -> dict:
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
                                    prediction_config_id: int) -> dict:
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
                                 poll_interval: float = 5.0) -> dict:
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
                          include_fitted_series: bool = False) -> dict:
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
        """
        body: dict[str, Any] = {
            "prediction_config_id": prediction_config_id,
            "verified": verified,
            "include_fitted_series": include_fitted_series,
        }
        if feature_overrides is not None:
            body["feature_overrides"] = feature_overrides
        return self._request(
            "POST", f"/api/v1/platforms/{platform_id}/symbolic-forecast", json=body)

    def residual_diagnosis(self, platform_id: int, *, prediction_config_id: int,
                           forecast_id: int | None = None,
                           value: float | None = None,
                           actual: float | None = None,
                           k: float | None = None) -> dict:
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
    def list(self) -> list[dict]:
        return self._request("GET", "/api/v1/api-keys")

    def create(self, *, scope: str = "platform", platform_id: int | None = None, name: str = "Default") -> dict:
        body: dict[str, Any] = {"scope": scope, "name": name}
        if platform_id is not None:
            body["platform_id"] = platform_id
        return self._request("POST", "/api/v1/api-keys", json=body)

    def revoke(self, key_id: int) -> dict:
        return self._request("DELETE", f"/api/v1/api-keys/{key_id}")


class ConnectorResource(_Resource):
    """Data-source connectors (e.g. FRED, Yahoo Finance).

    Connectors that pull from third-party providers may require *your own*
    credentials for that provider (e.g. a FRED API key). Pass them in the
    ``config`` dict — Ambertrace does not supply third-party keys on your behalf.
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

    For a CUMULATIVE control (a running count / sum / exposure over a history of
    prior actions), open a *session* instead of gating one action: the harness is
    the sole executor and accumulates the executed-action ledger, so the gate can
    prove the obligation over the *resulting* history (see :meth:`create_session`
    / :meth:`step`).

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

    def author(self, policy_text: str) -> dict:
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
        """
        return self._request(
            "POST", "/api/v1/agent-policy-gate/policy",
            json={"policy_text": policy_text})

    def status(self) -> dict:
        """The org's live agent-policy gate: the active policy text, the admitted
        controls (plain English), and the DECLARED INPUT fields an action must
        supply.

        Returns ``{"enabled": True, "platform": {...}|None, "policy_text": ...,
        "admitted_controls": [{"name", "description"}, ...], "input_fields":
        [{"name", "type", "enum_values"?, "min_value"?, "max_value"?,
        "description"?}, ...], "decision_vocabulary"?: {...}}``.

        ``input_fields`` is the contract for :meth:`authorize_action` / :meth:`step`
        - supply a value for each (under ``args`` or ``context``) so the gate
        returns a real permit/deny rather than rejecting an unknown/missing fact.
        """
        return self._request("GET", "/api/v1/agent-policy-gate")

    def examples(self) -> list[dict]:
        """The built-in example-policy library: ``[{"id", "domain_label",
        "title", "policy_text", "try_hint"}, ...]``. Each ``policy_text`` is a
        ready-to-author English policy you can pass straight to :meth:`author`."""
        return self._request("GET", "/api/v1/example-policies")

    def authorize_action(self, platform_id: int, *, tool: str,
                         args: dict | None = None,
                         context: dict | None = None) -> dict:
        """Gate ONE proposed tool-call against the verified policy - permit/deny
        WITH PROOF.

        ``args`` are the action's intrinsic fields; ``context`` carries ambient
        facts the policy reasons over (``args`` wins on a key collision). Supply a
        value for each of :meth:`status`'s ``input_fields``.

        Returns ``{"decision", "proof_checked", "proof_summary", "denied_reason",
        "deciding_rule"?, "certified_facts", "rejected_facts"}``. ``decision`` is
        the policy's verdict verb (``permit``/``deny``, or a custom verb the policy
        declares). Fail-closed: a rejected/missing fact, a proof-check failure, or
        an unavailable engine yields no permit - never a default-allow.

        For a CUMULATIVE obligation (class 2-4) this gates the action against an
        EMPTY history - use a :meth:`create_session` + :meth:`step` loop so the
        obligation is proven over the accumulated executed-action ledger.
        """
        action: dict = {"tool": tool, "args": args or {}}
        body: dict = {"action": action}
        if context is not None:
            body["context"] = context
        return self._request(
            "POST", f"/api/v1/platforms/{platform_id}/authorize-action", json=body)

    def create_session(self, *, platform_id: int,
                       goal: str | None = None) -> dict:
        """Open a mediated agent session bound to a verified agent-policy gate.

        Every action proposed via :meth:`step` is gated; the harness is the SOLE
        executor (no bypass) and accumulates the executed-action ledger, so a
        CUMULATIVE obligation (count / sum / exposure / band) is proven over the
        *resulting* history. Returns the session (``{"id", "platform_id", "goal",
        "trace": [...]}``)."""
        body: dict = {"platform_id": platform_id}
        if goal is not None:
            body["goal"] = goal
        return self._request("POST", "/api/v1/agent-sessions", json=body)

    def step(self, session_id: str, *, tool: str, args: dict | None = None,
             context: dict | None = None) -> dict:
        """Mediate ONE proposed action in a session: gate -> execute-on-permit /
        block-on-deny.

        The mediation invariant: an effect occurs IFF the gate returned permit
        with a checked proof. On a cumulative policy, the executed action's row
        joins the ledger so the next step's obligation folds over the resulting
        history. Returns ``{"session": {...}, "step": {"verdict": {...},
        "executed": bool, "effect": ...}}``."""
        action: dict = {"tool": tool, "args": args or {}}
        body: dict = {"action": action}
        if context is not None:
            body["context"] = context
        return self._request(
            "POST", f"/api/v1/agent-sessions/{session_id}/step", json=body)

    def get_session(self, session_id: str) -> dict:
        """Fetch a session and its full mediated step trace."""
        return self._request("GET", f"/api/v1/agent-sessions/{session_id}")


class JobResource(_Resource):
    def get(self, job_id: int) -> dict:
        """Fetch a job by id.

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

    def wait_for_job(self, job_id: int, *, timeout: int = 600, poll_interval: int = 5,
                     on_progress: Callable[[dict], None] | None = None,
                     stall_timeout: float | None = None) -> dict:
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
