"""Shared helpers for the AmbertraceAI SDK examples.

Loads configuration from the environment (or a local `.env` file sitting next to
the examples) and builds a ready-to-use :class:`AmbertraceAPI` client.

Environment variables:
    AMBERTRACE_API_KEY   Required. Your API key (starts with ``at_``).
    AMBERTRACE_BASE_URL  Optional. Defaults to https://app.ambertrace.ai
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from ambertraceai import AmbertraceAPI

DEFAULT_BASE_URL = "https://app.ambertrace.ai"
_ENV_PATH = Path(__file__).with_name(".env")


def _load_dotenv() -> None:
    """Minimal .env loader (no external dependency).

    Parses ``KEY=value`` lines; ignores blanks and ``#`` comments. Existing
    environment variables take precedence over the file.
    """
    if not _ENV_PATH.exists():
        return
    for raw in _ENV_PATH.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_client() -> AmbertraceAPI:
    """Build an AmbertraceAPI client from env / .env, or exit with guidance."""
    _load_dotenv()
    api_key = os.environ.get("AMBERTRACE_API_KEY")
    base_url = os.environ.get("AMBERTRACE_BASE_URL", DEFAULT_BASE_URL)
    if not api_key:
        sys.exit(
            "AMBERTRACE_API_KEY is not set.\n"
            "Create examples/.env with:\n"
            "    AMBERTRACE_API_KEY=at_your_key_here\n"
            "(copy examples/.env.example), or export it in your shell."
        )
    return AmbertraceAPI(base_url=base_url, api_key=api_key, timeout=60.0)


def wait_for_domain(api, domain_id: int, *, timeout: int = 180, poll_interval: int = 4) -> dict:
    """Poll a domain until its ontology build reaches a terminal status.

    Unlike platform builds, POST /domains/{id}/build-ontology runs in the
    background and does NOT return a job id, so wait_for_job can't be used —
    the domain transitions to 'active' on success or 'draft' on failure.
    """
    import time

    deadline = time.monotonic() + timeout
    while True:
        domain = api.domains.get(domain_id)
        status = domain.get("status", "")
        if status in ("active", "ready", "draft", "error"):
            return domain
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Domain {domain_id} ontology build did not finish within {timeout}s "
                f"(last status: {status})"
            )
        time.sleep(poll_interval)


def banner(title: str) -> None:
    print(f"\n{'=' * 70}\n {title}\n{'=' * 70}")


def step(msg: str) -> None:
    print(f"  → {msg}")
