"""AmbertraceAI Python SDK — convenience layer over the generated client."""

from __future__ import annotations

import time
from typing import Any

import httpx


class AmbertraceError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        super().__init__(message)


class _Resource:
    def __init__(self, client: httpx.Client):
        self._http = client

    def _request(self, method: str, path: str, **kwargs) -> Any:
        resp = self._http.request(method, path, **kwargs)
        body = resp.json()
        if resp.status_code >= 400:
            err = body.get("error", {})
            raise AmbertraceError(
                resp.status_code,
                err.get("code", "unknown"),
                err.get("message", resp.text),
            )
        return body.get("data", body)


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

    def graph(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/graph")


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


class JobResource(_Resource):
    def get(self, job_id: int) -> dict:
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

    def __init__(self, *, base_url: str, api_key: str, timeout: float = 30.0):
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

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
    def usage(self) -> UsageResource:
        return UsageResource(self._http)

    def wait_for_job(self, job_id: int, *, timeout: int = 600, poll_interval: int = 5) -> dict:
        """Poll a job until it reaches a terminal status or times out."""
        deadline = time.monotonic() + timeout
        while True:
            job = self.jobs.get(job_id)
            status = job.get("status", "")
            if status in ("ready", "active", "error", "failed", "completed"):
                return job
            if time.monotonic() >= deadline:
                raise TimeoutError(f"Job {job_id} did not complete within {timeout}s (last status: {status})")
            time.sleep(poll_interval)
