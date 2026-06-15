"""AmbertraceAI Python SDK — convenience layer over the generated client."""

from __future__ import annotations

import random
import time
from typing import Any

import httpx


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
    """

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Any = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details: list[dict] = _coerce_details(details)
        detail_str = _format_details(self.details)
        full = f"{message} ({detail_str})" if detail_str else message
        super().__init__(full)

    @property
    def rejected_facts(self) -> list[str]:
        """Convenience: the ``field`` names carried in ``details`` (may be empty)."""
        return [d["field"] for d in self.details if d.get("field")]


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
                raise AmbertraceError(
                    resp.status_code,
                    err.get("code", "unknown"),
                    err.get("message", resp.text),
                    err.get("details"),
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
        return self._request("POST", f"/api/v1/domains/{domain_id}/build-ontology")

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
    def list(self) -> list[dict]:
        return self._request("GET", "/api/v1/datasets")

    def get(self, dataset_id: int) -> dict:
        return self._request("GET", f"/api/v1/datasets/{dataset_id}")

    def upload(self, *, domain_id: int, file_path: str, name: str | None = None) -> dict:
        with open(file_path, "rb") as f:
            files = {"file": (name or file_path.split("/")[-1], f)}
            data = {"domain_id": str(domain_id)}
            if name:
                data["name"] = name
            return self._request("POST", "/api/v1/datasets/upload", files=files, data=data)

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

    def create(self, *, domain_id: int, dataset_id: int, name: str | None = None, **kwargs) -> dict:
        body: dict[str, Any] = {"domain_id": domain_id, "dataset_id": dataset_id, **kwargs}
        if name:
            body["name"] = name
        return self._request("POST", "/api/v1/platforms", json=body)

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
        (e.g. {"inflation": 5.0}); omit it to predict from the latest data.
        """
        body: dict[str, Any] = {"prediction_config_id": prediction_config_id, "explain": explain}
        if feature_overrides is not None:
            body["feature_overrides"] = feature_overrides
        return self._request("POST", f"/api/v1/platforms/{platform_id}/predict", json=body)

    def list_configs(self, platform_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/prediction-configs")

    def create_config(self, platform_id: int, **kwargs) -> dict:
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
        "n_adjustment_rules", "n_constraint_rules", "fire_rate"}`` when ``wait`` is
        True (the default). ``delta`` is neurosymbolic − neural (a positive
        ``delta.r2`` / negative ``delta.rmse`` means the symbolic layer helped).

        Pass ``wait=False`` for the raw 202 envelope (``{"job_id", "poll", ...}``)
        to poll the job yourself.
        """
        resp = self._request(
            "GET", f"/api/v1/platforms/{platform_id}/neurosymbolic-comparison",
            params={"prediction_config_id": prediction_config_id})
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
    """

    def __init__(self, *, base_url: str, api_key: str, timeout: float = 30.0,
                 warm: bool = True):
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
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

    def wait_for_job(self, job_id: int, *, timeout: int = 600, poll_interval: int = 5) -> dict:
        """Poll a job until it reaches a terminal status or times out.

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
        """
        deadline = time.monotonic() + timeout
        while True:
            job = self.jobs.get(job_id)
            status = job.get("status", "")
            if status in ("ready", "active", "error", "failed", "completed"):
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s (last status: {status})")
            # Keep the UI process (the health-gated one) warm alongside the API
            # status polls, so a long build doesn't let the machine suspend
            # mid-job. Best-effort.
            self._ping_health()
            time.sleep(poll_interval)
