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

    def fetch(self, *, url: str, domain_id: int, name: str | None = None) -> dict:
        body: dict[str, Any] = {"url": url, "domain_id": domain_id}
        if name:
            body["name"] = name
        return self._request("POST", "/api/v1/datasets/fetch", json=body)

    def quality(self, dataset_id: int) -> dict:
        return self._request("GET", f"/api/v1/datasets/{dataset_id}/quality")

    def clean(self, dataset_id: int) -> dict:
        return self._request("POST", f"/api/v1/datasets/{dataset_id}/clean")

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

    def status(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/status")

    def query(self, platform_id: int, *, query: str, explain: bool = True, **kwargs) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/query", json={"query": query, "explain": explain, **kwargs})

    def suggest_rules(self, platform_id: int, *, max_suggestions: int = 5) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/suggest-rules", json={"max_suggestions": max_suggestions})

    def list_suggestions(self, platform_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/suggestions")

    def graph(self, platform_id: int) -> dict:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/graph")


class PredictionResource(_Resource):
    def predict(self, platform_id: int, *, input_data: dict, config_id: int | None = None) -> dict:
        body: dict[str, Any] = {"input_data": input_data}
        if config_id is not None:
            body["config_id"] = config_id
        return self._request("POST", f"/api/v1/platforms/{platform_id}/predict", json=body)

    def list_configs(self, platform_id: int) -> list[dict]:
        return self._request("GET", f"/api/v1/platforms/{platform_id}/prediction-configs")

    def create_config(self, platform_id: int, **kwargs) -> dict:
        return self._request("POST", f"/api/v1/platforms/{platform_id}/prediction-configs", json=kwargs)

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


class JobResource(_Resource):
    def get(self, job_id: int) -> dict:
        return self._request("GET", f"/api/v1/jobs/{job_id}")


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
    def jobs(self) -> JobResource:
        return JobResource(self._http)

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
