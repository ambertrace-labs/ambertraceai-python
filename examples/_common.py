"""Shared helpers for the AmbertraceAI SDK examples.

Loads configuration from the environment (or a local `.env` file sitting next to
the examples) and builds a ready-to-use :class:`AmbertraceAPI` client.

Environment variables:
    AMBERTRACE_API_KEY   Required. Your API key (starts with ``at_``).
    AMBERTRACE_BASE_URL  Optional. Defaults to https://app.ambertrace.ai
"""

from __future__ import annotations

import logging
import os
import sys
import time
from typing import TYPE_CHECKING, Any

from ambertraceai import AmbertraceAPI, AmbertraceError

if TYPE_CHECKING:
    import argparse

from pathlib import Path

DEFAULT_BASE_URL = "https://app.ambertrace.ai"
DEFAULT_BUILD_TIMEOUT = 300
DEFAULT_POLL_INTERVAL = 3
DEFAULT_TAU = 0.6
DEFAULT_BUILD_RETRIES = 2
DEFAULT_RETRY_BACKOFF = 5

_READY_STATUSES = {"active", "ready", "trained", "completed"}
_FAILED_STATUSES = {"failed", "error"}

_ENV_PATH = Path(__file__).with_name(".env")

logger = logging.getLogger("ambertraceai.examples")


# ---------------------------------------------------------------------------
# Environment / client setup
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# CLI helpers (for domain demos 10+)
# ---------------------------------------------------------------------------

def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add --url / --api-key / -v flags every demo shares."""
    parser.add_argument(
        "--url",
        default=os.environ.get("AMBERTRACE_BASE_URL", DEFAULT_BASE_URL),
        help=f"API base URL (default: {DEFAULT_BASE_URL}, or AMBERTRACE_BASE_URL)",
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API key (at_...). Falls back to the AMBERTRACE_API_KEY env var.",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")


def add_verified_args(parser: argparse.ArgumentParser) -> None:
    """Verified-profile flags for the decision-domain demos."""
    parser.add_argument(
        "--standard",
        action="store_true",
        help="Build a standard (non-verified) platform instead of the verified profile.",
    )
    parser.add_argument(
        "--tau",
        type=float,
        default=DEFAULT_TAU,
        help=f"Verified-profile certified-fact confidence threshold τ in [0,1] "
        f"(default: {DEFAULT_TAU}). Ignored with --standard.",
    )


def configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )


def make_client(args: argparse.Namespace) -> AmbertraceAPI:
    """Build an authenticated client from parsed CLI args."""
    _load_dotenv()
    api_key = args.api_key or os.environ.get("AMBERTRACE_API_KEY")
    if not api_key:
        print(
            "ERROR: an API key is required. Pass --api-key at_... or set "
            "the AMBERTRACE_API_KEY environment variable.\n"
            "Create a key at https://app.ambertrace.ai under API Keys.",
            file=sys.stderr,
        )
        sys.exit(1)
    return AmbertraceAPI(base_url=args.url, api_key=api_key, timeout=120.0)


def run_demo(entry, args: argparse.Namespace) -> None:
    """Run ``entry(api, args)`` with shared logging + error handling."""
    configure_logging(args.verbose)
    api = make_client(args)
    try:
        entry(api, args)
    except AmbertraceError as exc:
        print(f"\nERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        api.close()


# ---------------------------------------------------------------------------
# Connectors
# ---------------------------------------------------------------------------

def fred_api_key() -> str | None:
    """The user-supplied FRED key (from FRED_API_KEY / .env), if present."""
    return os.environ.get("FRED_API_KEY")


def fetch_dataset(
    api: AmbertraceAPI,
    domain_id: int,
    connector_type: str,
    config: dict[str, Any],
) -> dict[str, Any]:
    """Ingest a dataset into a domain from a built-in connector.

    Connector types include ``fred``, ``yahoo``, ``coinbase`` (see
    ``api.connectors.list()``).
    """
    return api.datasets.fetch(domain_id=domain_id, connector_type=connector_type, config=config)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def banner(title: str) -> None:
    print(f"\n{'=' * 70}\n {title}\n{'=' * 70}")


def step(msg: str) -> None:
    print(f"  → {msg}")


def print_section(step_num: int, total: int, title: str) -> None:
    print(f"\n[{step_num}/{total}] {title}")


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _first(d: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in d and d[key] is not None:
            return d[key]
    return None


def _nested_id(d: dict[str, Any], *parents: str) -> Any:
    for parent in parents:
        child = d.get(parent)
        if isinstance(child, dict) and child.get("id") is not None:
            return child["id"]
    return None


def _await_job(
    api: AmbertraceAPI,
    job_id: int,
    what: str,
    timeout: int,
    poll_interval: int,
) -> dict[str, Any]:
    job = api.wait_for_job(int(job_id), timeout=timeout, poll_interval=poll_interval)
    status = job.get("status", "")
    if status in _FAILED_STATUSES:
        raise RuntimeError(f"{what} failed (job {job_id}: {job.get('error_message') or status})")
    return job


def _poll_status(fetch, timeout: int, poll_interval: int, what: str = "Build") -> None:
    deadline = time.monotonic() + timeout
    while True:
        status = (fetch() or {}).get("status", "")
        if status in _READY_STATUSES:
            return
        if status in _FAILED_STATUSES:
            raise RuntimeError(f"{what} failed (status: {status})")
        if time.monotonic() >= deadline:
            raise TimeoutError(f"{what} did not finish within {timeout}s (last status: {status})")
        time.sleep(poll_interval)


def _symbolic_trace(report: dict[str, Any]) -> dict[str, Any]:
    return (report.get("explanation", {}) or {}).get("symbolic_trace", {}) or {}


# ---------------------------------------------------------------------------
# Domain polling
# ---------------------------------------------------------------------------

def wait_for_domain(api, domain_id: int, *, timeout: int = 180, poll_interval: int = 4) -> dict:
    """Poll a domain until its ontology build reaches a terminal status."""
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


# ---------------------------------------------------------------------------
# Async build helpers
# ---------------------------------------------------------------------------

def build_ontology(
    api: AmbertraceAPI,
    domain_id: int,
    timeout: int = DEFAULT_BUILD_TIMEOUT,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    retries: int = DEFAULT_BUILD_RETRIES,
    retry_backoff: int = DEFAULT_RETRY_BACKOFF,
) -> dict[str, Any]:
    """Trigger an ontology build, wait for its job, and return the domain.

    Retries on a failed build job — the platform's ontology build is
    intermittently flaky (transient LLM failures) and re-triggering
    typically succeeds.
    """
    last_err: str | None = None
    for attempt in range(retries + 1):
        resp = api.domains.build_ontology(domain_id)
        job_id = _first(resp, "job_id") or _nested_id(resp, "job")
        if job_id is None:
            _poll_status(
                lambda: api.domains.get(domain_id), timeout, poll_interval,
                what=f"Ontology for domain {domain_id}",
            )
            return api.domains.get(domain_id)
        job = api.wait_for_job(int(job_id), timeout=timeout, poll_interval=poll_interval)
        if job.get("status") not in _FAILED_STATUSES:
            return api.domains.get(domain_id)
        last_err = job.get("error_message") or job.get("status")
        if attempt < retries:
            logger.warning(
                "Ontology build for domain %s failed (job %s: %s) — retrying %d/%d",
                domain_id, job_id, last_err, attempt + 1, retries,
            )
            time.sleep(retry_backoff)
    raise RuntimeError(
        f"Ontology build for domain {domain_id} failed after {retries + 1} attempts "
        f"(last: {last_err})"
    )


def build_platform(
    api: AmbertraceAPI,
    domain_id: int,
    dataset_id: int,
    timeout: int = DEFAULT_BUILD_TIMEOUT,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
    verified_profile: bool = False,
    verified_min_confidence: float | None = None,
) -> dict[str, Any]:
    """Create a platform and wait for its build job to finish."""
    extra: dict[str, Any] = {}
    if verified_profile:
        extra["verified_profile"] = True
        if verified_min_confidence is not None:
            extra["verified_min_confidence"] = verified_min_confidence
    resp = api.platforms.create(domain_id=domain_id, dataset_id=dataset_id, **extra)
    platform_id = _first(resp, "id", "platform_id") or _nested_id(resp, "platform")
    job_id = _first(resp, "job_id") or _nested_id(resp, "build_job", "job")

    if job_id is not None:
        _await_job(api, job_id, f"Platform build for domain {domain_id}", timeout, poll_interval)
    elif platform_id is not None:
        _poll_status(
            lambda: api.platforms.status(int(platform_id)), timeout, poll_interval,
            what=f"Platform {platform_id}",
        )

    if platform_id is None:
        raise RuntimeError(f"Platform creation returned no id: {resp!r}")
    return api.platforms.get(int(platform_id))


# ---------------------------------------------------------------------------
# Pretty-printing: data inspection
# ---------------------------------------------------------------------------

def print_dataset(dataset: dict[str, Any]) -> None:
    print(
        f"  Dataset {dataset.get('id')}: {dataset.get('row_count', 0)} rows, "
        f"{dataset.get('column_count', 0)} columns"
    )
    schema = dataset.get("schema_info") or {}
    columns = schema.get("columns", [])
    if columns:
        types = ", ".join(f"{c.get('name')}({c.get('inferred_type')})" for c in columns[:6])
        print(f"  Schema: {types}...")


def print_ontology(domain: dict[str, Any], limit: int = 8) -> None:
    ontology = domain.get("ontology") or {}
    entities = ontology.get("entities", [])
    constraints = ontology.get("constraints", [])
    print(f"  Ontology ready: {len(entities)} entities, {len(constraints)} rules")
    for entity in entities[:limit]:
        print(f"    Entity: {entity.get('name', '?')}")
    for constraint in constraints[:limit]:
        desc = (constraint.get("description") or "")[:60]
        print(f"    Rule:   {constraint.get('name', '?')}: {desc}")


def print_quality(quality: dict[str, Any]) -> None:
    def _score(value: Any) -> float:
        if isinstance(value, dict):
            return float(value.get("score", 0.0))
        return float(value or 0.0)

    print(f"  Overall:      {_score(quality.get('overall_score')):.0%}")
    print(f"  Completeness: {_score(quality.get('completeness')):.0%}")
    print(f"  Consistency:  {_score(quality.get('consistency')):.0%}")
    print(f"  Uniqueness:   {_score(quality.get('uniqueness')):.0%}")
    for rec in quality.get("recommendations", []):
        print(f"  -> {rec}")


def print_graph(graph: dict[str, Any], limit: int = 10) -> None:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    print(f"  {graph.get('total_nodes', len(nodes))} nodes, {len(edges)} edges")
    for node in nodes[:limit]:
        uid = node.get("node_uuid")
        edge_count = sum(
            1 for e in edges if e.get("source_uuid") == uid or e.get("target_uuid") == uid
        )
        print(f"    {node.get('label')} ({node.get('node_type')}) -- {edge_count} connections")


# ---------------------------------------------------------------------------
# Amber Report
# ---------------------------------------------------------------------------

def symbolic_rules(report: dict[str, Any]) -> list[dict[str, Any]]:
    return _symbolic_trace(report).get("rules", [])


def rules_fired_count(report: dict[str, Any]) -> int:
    return _symbolic_trace(report).get("rules_fired", 0)


def rules_evaluated_count(report: dict[str, Any]) -> int:
    return _symbolic_trace(report).get("rules_evaluated", 0)


def print_amber_report(report: dict[str, Any]) -> None:
    """Render an Amber Report — the headline explainability feature."""
    explanation = report.get("explanation", {}) or {}
    confidence = explanation.get("confidence", {}) or {}
    neural_nodes = (explanation.get("neural_trace", {}) or {}).get("nodes", [])
    rules = symbolic_rules(report)
    fired = rules_fired_count(report)
    evaluated = rules_evaluated_count(report)

    print(f"\n{'=' * 70}")
    print("AMBER REPORT")
    print("=" * 70)
    print(f"Query: {report.get('query', '')}")
    print(f"Confidence: {confidence.get('overall', 0.0):.0%}")
    print(
        f"  Neural:   {confidence.get('neural_confidence', 0.0):.0%}"
        f" (weight {confidence.get('neural_weight', 0.0)})"
    )
    print(
        f"  Symbolic: {confidence.get('symbolic_confidence', 0.0):.0%}"
        f" (weight {confidence.get('symbolic_weight', 0.0)})"
    )
    if neural_nodes:
        top = neural_nodes[0]
        print(
            f"Neural nodes: {len(neural_nodes)} "
            f"(top: {top.get('label')} @ {top.get('relevance_score', 0.0):.3f})"
        )
    else:
        print("Neural nodes: 0")
    print(f"Rules: {fired}/{evaluated} fired")
    connected = (explanation.get("graph_trace", {}) or {}).get("connected_nodes", 0)
    print(f"Graph: {connected} connected nodes")

    if rules:
        print(f"\nSymbolic Rules ({fired}/{evaluated} fired):")
        for rule in rules:
            status = "FIRED" if rule.get("fired") else "not fired"
            action = f" [{rule['action_type']}]" if rule.get("action_type") else ""
            marker = ">>>" if rule.get("fired") else "   "
            name, rtype = rule.get("rule_name"), rule.get("rule_type")
            print(f"  {marker} {name} ({rtype}): {status}{action}")
            if rule.get("explanation"):
                print(f"      {rule['explanation']}")

    if fired:
        print("\n  [Symbolic reasoning contributed to this answer]")
    else:
        print("\n  [Answer based on neural retrieval only -- no rules fired]")

    rejected = explanation.get("rejected_facts")
    if report.get("proof_checked") is not None:
        mark = "CHECKED" if report.get("proof_checked") else "NOT CERTIFIED"
        print(f"\n  Proof: {mark}")
        if report.get("proof_summary"):
            print(f"    {report['proof_summary']}")
    if rejected:
        print(f"  Rejected facts (below τ): {rejected}")

    answer = report.get("answer") or ""
    print(f"\nAnswer: {answer[:200]}...")
    print("=" * 70)


def query_and_report(api: AmbertraceAPI, platform_id: int, query: str) -> None:
    """Query a platform and print the Amber Report.

    On a verified platform a query that can't be certified is fail-closed
    refused (HTTP 503): we surface that as a verified outcome rather than
    letting it abort the run.
    """
    try:
        report = api.platforms.query(platform_id, query=query)
    except AmbertraceError as exc:
        fail_closed = getattr(exc, "status_code", None) == 503 or \
            getattr(exc, "code", "") == "service_unavailable"
        if fail_closed:
            print(f"\n{'=' * 70}\nAMBER REPORT\n{'=' * 70}")
            print(f"Query: {query}")
            print("\n  [VERIFIED: fail-closed — the reasoning engine could not certify a")
            print(f"   result, so no answer was returned. ({exc})]")
            print("=" * 70)
            return
        raise
    print_amber_report(report)


# ---------------------------------------------------------------------------
# Prediction helpers
# ---------------------------------------------------------------------------

def prediction_values(prediction: dict[str, Any]) -> tuple[float, float, float]:
    """Return (value, lower_bound, upper_bound) from a predict() payload."""
    pred = prediction.get("prediction", prediction) or {}
    value = float(pred.get("value", 0.0))
    lower = float(pred.get("lower_bound", value))
    upper = float(pred.get("upper_bound", value))
    return value, lower, upper


def print_prediction_explanation(prediction: dict[str, Any]) -> None:
    expl = prediction.get("explanation")
    if not isinstance(expl, dict):
        return

    info = expl.get("model_info")
    if isinstance(info, dict):
        print(f"  Model: {info.get('model_type', '?')} (tier {info.get('tier', '?')})")
        for key, val in (info.get("metrics", {}) or {}).items():
            print(f"    {key}: {val:.4f}" if isinstance(val, float) else f"    {key}: {val}")

    fi = expl.get("feature_importance")
    pairs: list[tuple[str, Any]] = []
    if isinstance(fi, dict):
        pairs = list(fi.items())
    elif isinstance(fi, list):
        for item in fi:
            if isinstance(item, (list, tuple)) and len(item) == 2:
                pairs.append((item[0], item[1]))
            elif isinstance(item, dict):
                pairs.append(
                    (
                        item.get("feature", item.get("name", "?")),
                        item.get("importance", item.get("value", 0)),
                    )
                )
    if pairs:
        pairs.sort(key=lambda x: abs(x[1]) if isinstance(x[1], (int, float)) else 0, reverse=True)
        print("  Feature importance:")
        for feat, imp in pairs[:5]:
            print(f"    {feat}: {imp:.4f}" if isinstance(imp, float) else f"    {feat}: {imp}")

    if expl.get("rule_results"):
        print(f"  Rule adjustments: {expl['rule_results']}")

    text = expl.get("explanation")
    if isinstance(text, str) and text:
        print(f"  AI explanation: {text[:200]}...")


def train_prediction_model(
    api: AmbertraceAPI,
    platform_id: int,
    config_id: int,
    timeout: int = DEFAULT_BUILD_TIMEOUT,
    poll_interval: int = DEFAULT_POLL_INTERVAL,
) -> dict[str, Any]:
    """Train a prediction config and wait until it reports a trained status."""
    resp = api.predictions.train(platform_id, config_id)
    job_id = _first(resp, "job_id") or _nested_id(resp, "job")
    if job_id is not None:
        _await_job(api, job_id, f"Training for config {config_id}", timeout, poll_interval)
        return _find_config(api, platform_id, config_id)

    deadline = time.monotonic() + timeout
    while True:
        config = _find_config(api, platform_id, config_id)
        status = config.get("status", "")
        if status in _READY_STATUSES:
            return config
        if status in _FAILED_STATUSES:
            raise RuntimeError(
                f"Training failed for config {config_id} "
                f"({config.get('error_message') or status})"
            )
        if time.monotonic() >= deadline:
            raise TimeoutError(
                f"Training for config {config_id} did not finish within {timeout}s "
                f"(last status: {status})"
            )
        time.sleep(poll_interval)


def _find_config(api: AmbertraceAPI, platform_id: int, config_id: int) -> dict[str, Any]:
    for config in api.predictions.list_configs(platform_id):
        if config.get("id") == config_id:
            return config
    raise RuntimeError(f"Prediction config {config_id} not found on platform {platform_id}")
