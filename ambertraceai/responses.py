"""Return-shape ``TypedDict``s for the convenience layer.

(Module named ``responses`` — NOT ``types`` — so it never collides with the
generated client's own ``ambertraceai/types.py``, which defines ``Unset`` /
``Response`` / ``File`` and is imported across the generated models. The overlay
is copied over the generated tree at build time, so a ``types.py`` here would
clobber that and break the client.)

These annotate what each :class:`~ambertraceai.convenience` method returns so an
IDE can autocomplete the fields and a type-checker can catch a typo
(``result["desicion"]``) — WITHOUT changing anything at runtime. Every
convenience method still returns a plain ``dict`` / :class:`AttrDict`, so
``result["answer"]`` / ``result.answer`` / ``.get(...)`` / ``**spread`` /
``json.dumps(...)`` keep working byte-for-byte. This is purely additive typing.

Design notes:

* ``TypedDict`` is a STRUCTURAL type only. At runtime a ``TypedDict`` *is* a
  ``dict`` — annotating ``-> QueryResult`` does not wrap or validate anything;
  the object returned is the same ``AttrDict`` as before. So this module can
  never break a consumer's ``[...]`` access.
* ``total=False`` marks a shape whose fields are all OPTIONAL — used where the
  API only sends a field conditionally (e.g. ``explanation`` only when
  ``explain=True``, ``denied_reason`` only on a deny). Required fields (always
  present) live in a separate base the shape inherits from.
* Where the response is genuinely OPEN / dynamic (an ``explanation`` blob whose
  keys depend on the platform, a raw ``prediction`` sub-object, a CRUD echo, a
  templates/eval-config/usage/graph/drift payload the public API does not pin a
  schema for), the alias :data:`JsonDict` (``dict[str, Any]``) is used rather
  than forcing a rigid shape the server may legitimately extend. Those are
  called out in the convenience docstrings / the audit.
"""

from __future__ import annotations

from typing import Any, Required, TypedDict

# An open JSON object whose keys are not pinned by the public contract. Used
# for CRUD echoes, dynamic sub-blocks (``explanation``, the raw ``prediction``),
# and payloads the API may extend. Kept deliberately permissive so a typed
# return never lies about a shape the server is free to grow.
JsonDict = dict[str, Any]


# --- Resource records (derived from the generated OpenAPI models) ----------

class DomainOut(TypedDict, total=False):
    """A domain record (``domains.get`` / ``create`` / ``update`` / an item of
    ``domains.list``). Mirrors the ``DomainOut`` OpenAPI model."""

    id: Required[int]
    name: Required[str]
    organisation_id: Required[str]
    status: Required[str]
    description: str | None
    visibility: str
    owner_user_id: int | None
    team_id: int | None
    created_at: str | None
    updated_at: str | None


class DatasetOut(TypedDict, total=False):
    """A dataset record (``datasets.get`` / ``upload`` / an item of
    ``datasets.list``). Mirrors the ``DatasetOut`` OpenAPI model. Note the
    async connector fetches (``fetch`` / ``fetch_multi`` / ``clean``) return
    this shape with ``status == "processing"`` until the fetch settles — poll
    ``datasets.get`` until ``status == "ready"``."""

    id: Required[int]
    name: Required[str]
    domain_id: Required[int]
    organisation_id: Required[str]
    source_type: Required[str]
    status: Required[str]
    row_count: int | None
    column_count: int | None
    decision_column: str | None
    description: str | None
    schema_info: JsonDict | None
    relation_name: str | None
    relation_join_key: str | None
    created_at: str | None
    updated_at: str | None


class PlatformOut(TypedDict, total=False):
    """A platform record (``platforms.get`` / an item of ``platforms.list``).
    Mirrors the ``PlatformOut`` OpenAPI model. ``build_quality`` is the
    structural-health summary (see :class:`BuildQuality`).

    ``error_message`` (str | None) — present when the platform build failed;
    carries the human-readable failure reason (persisted at build time).
    ``None`` on a healthy platform."""

    id: Required[int]
    name: Required[str]
    domain_id: Required[int]
    organisation_id: Required[str]
    status: Required[str]
    version: int
    visibility: str
    verified_profile: bool
    verified_min_confidence: float | None
    build_quality: BuildQuality | None
    config: JsonDict | None
    neural_config: JsonDict | None
    error_message: str | None
    description: str | None
    owner_user_id: int | None
    team_id: int | None
    created_at: str | None
    updated_at: str | None


class PlatformStatusOut(TypedDict, total=False):
    """A platform status record (``platforms.status``). Mirrors
    ``PlatformStatusOut``."""

    platform_id: Required[int]
    name: Required[str]
    status: Required[str]
    version: int


class BuildQualityCheck(TypedDict, total=False):
    """One structural-health check inside :class:`BuildQuality`."""

    id: str
    severity: str  # "blocking" | "warning" | "info"
    ok: bool
    detail: str
    items: list[str]


class BuildQuality(TypedDict, total=False):
    """The customer-facing build-quality summary
    (``platforms.build_quality`` / ``wait_for_job(...)["result"]["build_quality"]``)."""

    status: str  # "ok" | "warnings" | "needs_review"
    checks: list[BuildQualityCheck]


class StatedConstraintFinding(TypedDict, total=False):
    """A single finding from the stated-constraint faithfulness diagnostic
    (``domains.get(id)["ontology"]["stated_constraint_diagnostics"]``).

    Each finding reports a constraint the domain description STATES (e.g.
    "debt must not exceed 40% of income") that no rule in the built program
    encodes. Advisory only -- it never gates the build. Fields:

    - ``type``: always ``"stated_constraint_not_encoded"``.
    - ``comparison_field`` / ``coefficient_field``: the two data columns in
      the stated relation (from the customer's own description + data).
    - ``coefficient``: the numeric multiplier (e.g. 0.4 for "40%").
    - ``direction``: the comparison direction (e.g. ``"lte"``).
    - ``sentence``: the source sentence from the domain description.
    """

    type: str
    comparison_field: str
    coefficient_field: str
    coefficient: float | None
    direction: str | None
    sentence: str | None


class GenerationDiagnostics(TypedDict, total=False):
    """The build-generation diagnostics behind :class:`BuildQuality`
    (``wait_for_job(...)["result"]["generation_diagnostics"]``)."""

    rule_count: int
    classifier_count: int
    verdict_conclusion_count: int
    connected_restrictive_count: int
    can_decide_adversely: bool
    decision_coverage_warnings: list[str]
    non_discriminating_rules: list[str]
    unbound_references: list[Any]
    orphan_derived: list[str]


class JobResult(TypedDict, total=False):
    """A build/ontology job's ``result`` payload (present on a platform build)."""

    build_quality: BuildQuality
    generation_diagnostics: GenerationDiagnostics


class JobOut(TypedDict, total=False):
    """A job record (``jobs.get`` / the dict ``wait_for_job`` returns). Mirrors
    the ``JobOut`` OpenAPI model. ``result`` carries the build-quality /
    generation-diagnostics for a platform build."""

    id: Required[int]
    status: Required[str]
    type: str  # the OpenAPI model exposes ``type_``; the JSON key is ``type``
    progress: int | None
    step: str | None
    error_message: str | None
    result: JobResult | None
    created_at: str | None
    updated_at: str | None


class PredictionConfigOut(TypedDict, total=False):
    """A prediction-config record (``predictions.create_config`` /
    ``list_configs`` items / the trained config ``train`` returns). Mirrors the
    ``PredictionConfigOut`` OpenAPI model. ``output_space`` /
    ``resolved_target_transform`` echo the resolved forecast space."""

    id: int
    platform_id: int
    organisation_id: str
    status: str
    target_field: str
    model_type: str
    model_tier: str
    eval_metric: str
    mode: str  # "cross_sectional" | "timeseries"
    autoregressive: str
    max_ar_lag: int | None
    time_index_field: str | None
    horizon: int | None
    frequency: str | None
    feature_fields: list[str] | None
    feature_config: JsonDict | None
    backtest_config: JsonDict | None
    eval_metric_config: JsonDict | None
    output_space: str | None  # "level" | "change"
    resolved_target_transform: str | None
    target_transform_reason: str | None
    error_message: str | None
    created_at: str | None
    updated_at: str | None


class ForecastOut(TypedDict, total=False):
    """A stored forecast record (item of ``predictions.list_predictions``).
    Mirrors the ``ForecastOut`` OpenAPI model."""

    id: int
    prediction_model_id: int
    value: float
    actual_value: float | None
    lower_bound: float | None
    upper_bound: float | None
    horizon: int | None
    forecast_date: str | None
    features_used: JsonDict | None
    rule_adjustments: JsonDict | None
    created_at: str | None


# --- Query / decision returns (documented only in docstrings) --------------

# --- explanation sub-shapes (the dense-reward / audit contract) ------------
# These pin the documented ``explanation`` sub-blocks a verified-platform query
# returns. They are ADDITIVE typing
# only — at runtime ``explanation`` is still a plain dict the server may extend
# (hence ``total=False`` throughout and an open ``JsonDict`` fall-through for
# unmodelled keys); annotating them lets a consumer read
# ``explanation["symbolic_trace"]["rules"][i]["fired"]`` with autocomplete +
# type-checking instead of guessing at an ``Any``.


class RuleFiring(TypedDict, total=False):
    """One rule's evaluation in ``symbolic_trace.rules[]``. BOTH fired and
    unfired rules are listed (the dense-reward "which fired vs. which existed"
    signal). On a VERIFIED platform ``fired`` reflects the KERNEL-CERTIFIED
    firing set (reconciled against ``proof.firings``), not the engine
    self-report."""

    rule_id: int | None
    rule_name: Required[str]  # stable identifier
    rule_type: str  # e.g. "derive" | "constraint"
    action_type: str | None
    fired: Required[bool]
    required: bool  # hard obligation (a `require` leaf or a deny-family verdict)?
    explanation: str


class SymbolicTrace(TypedDict, total=False):
    """``explanation.symbolic_trace`` — the per-criterion firing breakdown."""

    description: str
    rules_evaluated: int
    rules_fired: int
    rules: list[RuleFiring]


class CertifiedFact(TypedDict, total=False):
    """One accepted fact in ``explanation.certified_facts`` (verified platform):
    its value, fused confidence, and its provenance certificate."""

    field: Required[str]
    value: Any
    confidence: float
    schema_ok: bool
    witness_invalid: bool
    reasons: list[str]
    source: str
    certificate: JsonDict


class CertifiedFactSummary(TypedDict, total=False):
    """``explanation.certified_fact_summary`` — per-query fact-gate counts."""

    accepted: int
    emitted: int
    rejected: int
    witness_invalid: int


class RejectedFact(TypedDict, total=False):
    """One fact rejected at the certified-fact gate.

    Carried on BOTH surfaces: the 200 ``explanation.rejected_facts`` and
    the fail-closed 503 error body's ``rejected_facts`` (read via
    ``AmbertraceError.rejected_facts``). ``field`` is the rejected field name,
    ``value`` the offending value (``None`` when the reject carries none, e.g. a
    grace/absence reject), and ``reasons`` the machine-readable rejection
    reasons (e.g. out-of-domain, below-threshold)."""

    field: Required[str]
    value: Any
    reasons: list[str]


class Confidence(TypedDict, total=False):
    """``explanation.confidence`` — fused neural+symbolic confidence.

    ``overall`` measures reasoning completeness (rules fired + KB relevance)
    and is approximately constant per platform.

    ``decision_margin`` (when present) is the **per-call** boundary-margin
    confidence: a value in [0, 1] measuring how far this input's facts are
    from the nearest fired numeric threshold (the label-flip boundary).
    0 = exactly at boundary, 1 = maximally far.  It varies with every call
    and is certified (derived from the same facts/firings as the proof).
    Present only when fired rules contain numeric threshold comparisons
    (gt/lt/gte/lte).

    **Scope:** ``decision_margin`` is the tightest (minimum) boundary margin
    across ALL fired numeric-threshold leaves, NOT restricted to the
    decision-determining/binding rules.  A near-boundary fired-but-overridden
    rule can lower the reported margin even when it did not determine the
    final decision.

    ``decision_margin_basis`` lists the per-leaf inputs used to compute the
    margin (field, operator, actual value, threshold, leaf_margin).
    """

    overall: float
    neural_confidence: float
    symbolic_confidence: float
    neural_weight: float
    symbolic_weight: float
    symbolic_normaliser: int
    decision_margin: float
    decision_margin_basis: list[dict[str, object]]


class Proof(TypedDict, total=False):
    """``explanation.proof`` — the machine-checked derivation certificate
    (verified platform)."""

    inputs: JsonDict
    derived: list[JsonDict]  # [{field, value, by, stratum}]
    firings: list[JsonDict]  # [{rule, action, stratum}]
    facts: JsonDict


class QueryExplanation(TypedDict, total=False):
    """``QueryResult.explanation`` (present with ``explain=True``) — a DOCUMENTED,
    VERSIONED trace. ``schema_version`` pins the shape; ``symbolic_trace`` /
    ``certified_facts`` / ``certified_fact_summary`` / ``confidence`` / ``proof``
    are the dense-reward / audit substrate. Additional platform-shaped keys
    (``neural_trace`` / ``graph_trace`` / ``relation_provenance`` / …) may be
    present; the ``TypedDict`` is ``total=False`` and the server may extend it."""

    schema_version: int
    symbolic_trace: SymbolicTrace
    certified_facts: list[CertifiedFact]
    certified_fact_summary: CertifiedFactSummary
    rejected_facts: list[RejectedFact]
    confidence: Confidence
    proof: Proof
    decision: JsonDict  # {decision, deciding_rules: [{rule, reason}]}
    proof_checked: bool
    proof_summary: str
    vocabulary_declared: bool


class QueryResult(TypedDict, total=False):
    """The shape ``platforms.query`` returns. ``answer`` / ``decision`` are the
    verdict; ``explanation`` (present with ``explain=True``) is the documented,
    versioned :class:`QueryExplanation` trace — pin ``explanation["schema_version"]``
    and read the dense-reward substrate (``symbolic_trace.rules[]``,
    ``certified_facts``, ``confidence``, ``proof``) from typed sub-shapes."""

    answer: Required[str]
    platform_id: Required[int]
    query: Required[str]
    decision: str | None
    proof_checked: bool | None
    proof_summary: str | None
    vocabulary_declared: bool | None
    explanation: QueryExplanation


class AuthorizeActionResult(TypedDict, total=False):
    """The permit/deny verdict ``agent_policy.authorize_action`` returns (and
    the ``verdict`` inside ``step``'s result). BRANCH on ``outcome`` — it
    separates the three non-permits ``decision`` / ``permitted`` conflate."""

    decision: Required[str]  # policy verdict verb ("permit"/"deny"/custom)
    permitted: Required[bool]
    proof_checked: Required[bool]
    outcome: Required[str]  # "permit" | "deny" | "indeterminate" | "unavailable"
    proof_summary: str
    denied_reason: str | None
    deciding_rule: Any
    certified_facts: list[Any]
    rejected_facts: list[Any]
    missing_inputs: list[str]
    stalled_stage: str | None
    query_diagnostics: JsonDict


class SessionStep(TypedDict, total=False):
    """The ``step`` block of a :class:`StepResult`."""

    verdict: AuthorizeActionResult
    executed: bool
    effect: Any


class StepResult(TypedDict, total=False):
    """What ``agent_policy.step`` returns: the updated session + the mediated
    step (its ``verdict`` has the :class:`AuthorizeActionResult` shape)."""

    session: SessionResult
    step: SessionStep


class SessionResult(TypedDict, total=False):
    """A mediated agent session (``create_session`` / ``get_session``)."""

    id: str
    platform_id: int
    goal: str | None
    trace: list[Any]


class AdmittedControl(TypedDict, total=False):
    """One admitted control in an :class:`AuthorResult` / :class:`AgentPolicyStatus`."""

    name: str
    description: str
    kind: str


class RejectedProposal(TypedDict, total=False):
    """One rejected proposal in an :class:`AuthorResult` (surfaced, never dropped)."""

    name: str
    reason: str


class AuthorResult(TypedDict, total=False):
    """What ``agent_policy.author`` returns: the built gate + the admitted /
    rejected read-back. ``platform`` is the built gate platform record."""

    platform: PlatformOut
    admitted: list[AdmittedControl]
    rejected: list[RejectedProposal]
    policy_text: str
    decision_vocabulary: JsonDict


class InputField(TypedDict, total=False):
    """A declared input field in :class:`AgentPolicyStatus`."""

    name: str
    type: str
    enum_values: list[Any]
    min_value: float
    max_value: float
    description: str


class RelationDecl(TypedDict, total=False):
    """A declared relation in :class:`AgentPolicyStatus`."""

    name: str
    columns: list[JsonDict]
    max_rows: int


class AgentPolicyStatus(TypedDict, total=False):
    """What ``agent_policy.status`` returns: the org's live gate + the declared
    input-field / relation contract for ``authorize_action`` / ``step``."""

    enabled: bool
    platform: PlatformOut | None
    policy_text: str
    admitted_controls: list[AdmittedControl]
    input_fields: list[InputField]
    relations: list[RelationDecl]
    decision_vocabulary: JsonDict


# --- Prediction returns ----------------------------------------------------

class DiscoverySummary(TypedDict, total=False):
    """The summary ``discover_prediction_rules`` returns (``wait=True``)."""

    prediction_config_id: int
    total_accepted: int
    total_rejected: int
    rounds: int
    converged: bool
    convergence_reason: str


class DiscoveredRule(TypedDict, total=False):
    """One accepted rule in :class:`DiscoveredRules`."""

    id: int
    name: str
    description: str
    rule_type: str
    condition: JsonDict
    action: JsonDict
    priority: int
    is_active: bool
    fire_rate: float
    delta: float
    eval_metric: str
    discovery_round: int


class DiscoveredRules(TypedDict, total=False):
    """What ``discovered_prediction_rules`` returns."""

    platform_id: int
    prediction_config_id: int
    accepted_rules: list[DiscoveredRule]
    total_accepted: int


class MetricBlock(TypedDict, total=False):
    """A ``{r2, rmse, mae, n}`` metric block in :class:`NeurosymbolicComparison`."""

    r2: float
    rmse: float
    mae: float
    n: int


class ComparisonSeriesPoint(TypedDict, total=False):
    """One per-period point of a :class:`NeurosymbolicComparison` ``series``."""

    index: int
    time: str
    actual: float
    neural: float
    neurosymbolic: float
    rule_fired: bool


class NeurosymbolicComparison(TypedDict, total=False):
    """What ``neurosymbolic_comparison`` returns (``wait=True``)."""

    platform_id: int
    prediction_config_id: int
    target: str
    neural: MetricBlock
    neurosymbolic: MetricBlock
    delta: JsonDict  # {"r2": ..., "rmse": ...}
    n_adjustment_rules: int
    n_constraint_rules: int
    n_pending_rules: int
    fire_rate: float
    mode: str  # "active" | "preview_pending"
    series: list[ComparisonSeriesPoint]


class ForecastBlock(TypedDict, total=False):
    """The ``forecast`` sub-block of a :class:`SymbolicForecastResult`."""

    value: float
    lower: float
    upper: float
    interval_basis: str


class ProbabilityBasis(TypedDict, total=False):
    """The ``probability_basis`` on a :class:`PredictionRecord` — how the
    certified probability was derived + whether it certified."""

    method: str
    interval_basis: str
    interval_z: float
    direction: str  # "up" | "down"
    sigma: float
    threshold: float
    reason: str


class PredictionRecord(TypedDict, total=False):
    """The canonical Stage-A ``prediction_record`` on a
    :class:`SymbolicForecastResult` — a ready-to-persist, LEVEL-space,
    proof-carrying record. The decision layer reads ``value`` / ``interval`` /
    ``probability`` / ``fired_signals``; ``probability`` is ``None`` unless
    ``probability_certified`` (fail-closed). ``probability_computable`` is
    ``False`` when the threshold equals the value (no directional signal).

    ``neural_model_name`` (str | None) — the registry key of the neural-tier
    winner (e.g. ``"gbt"``); echoed from the forecast.

    ``neural_holdout_skill`` (float | None) — the holdout
    ``skill_vs_persistence`` of the winning neural model."""

    value: Required[float]
    probability: Required[float | None]
    probability_certified: Required[bool]
    probability_computable: Required[bool]
    name: str
    model_id: str
    as_of: str | None
    target_field: str
    horizon: int
    interval: JsonDict  # {"lower", "upper", "basis"}
    probability_basis: ProbabilityBasis
    fired_signals: list[Any]
    top_drivers: list[JsonDict]
    proof_ref: JsonDict
    why_certification: JsonDict
    forecast_tier: str | None
    neural_confidence_tau: float | None
    neural_model_name: str | None
    neural_holdout_skill: float | None
    sector: str | None
    period: str | None
    entity: str | None


class SymbolicForecastResult(TypedDict, total=False):
    """What ``symbolic_forecast`` returns. ``why`` (== ``accepted_drivers``) is
    the explanation; ``prediction_record`` is the canonical Stage-A output.
    ``why_certification`` (verified) / ``fitted_series`` (opt-in) are open
    blocks typed as :data:`JsonDict`.

    ``hit_rate_alpha`` (float) — the significance level used for the binomial
    hit-rate pre-filter that gates driver admission. Echoes the
    server's ACTUAL fitted value (default 0.05, overridable via
    ``AMBERTRACE_PREDICTION_HIT_RATE_ALPHA``).

    ``sign_base_rate`` (float) — the target's own dominant-sign base rate
    (fraction of fit-window periods moving in its more-common direction).
    Every accepted driver's hit-rate must beat this at ``hit_rate_alpha``.

    ``neural_model_name`` (str | None) — the registry key of the neural-tier
    winner selected during fit (e.g. ``"gbt"``, ``"ridge"``, ``"lasso"``,
    ``"lstm"``, ``"transformer"``); ``None`` when no neural model was fitted.

    ``neural_holdout_skill`` (float | None) — the holdout
    ``skill_vs_persistence`` of the winning neural model; ``None`` when no
    neural model was fitted.

    ``prediction_react_trajectory`` (dict | None) — the ReAct proposer's
    trajectory summary when the prediction was built via the agentic
    proposer loop. Carries ``total_turns``, ``best_turn``, ``best_skill``,
    ``skill_trajectory`` (list of per-turn skills), ``stop_reason``, and
    ``screen`` (the holdout screen applied). ``None`` when the proposer was
    not used.

    ``prediction_screen_enabled`` (bool) — whether the holdout prediction
    screen was active for this forecast.

    **fitted_series per-point rule-firing annotations:**

    When ``include_fitted_series=True``, each point in
    ``fitted_series.series[i]`` carries:

    ``fired_rules`` (list[str]) — the names of admitted driver-rules whose
    condition held on that holdout row. Empty on ``baseline_anchor`` points
    (no driver fired).

    ``rule_layer_predicted`` (float) — the symbolic rule-layer-only
    prediction: anchor + sum of fired effects, where anchor is the
    forecaster's per-point composition base (persistence under
    ``baseline_mode='persistence'``; GBT prediction under ``'neural'``;
    drift-projected level under ``'drift'``). Equals the anchor on
    zero-fire points.

    **per_tier_skill per-tier trading metrics:**

    When ``include_fitted_series=True`` and the config has a ``frequency``
    set, ``per_tier_skill`` carries per-tier trading metrics alongside the
    existing skill metrics.  Each tier entry (keyed by ``forecast_tier``
    label) and the ``all_points`` entry additionally contain:

    ``directional_pnl`` (float | None), ``sharpe_ratio`` (float | None),
    ``hit_rate`` (float | None), ``max_drawdown`` (float).

    Three component-layer entries are added:

    ``composed`` — trading metrics computed over ALL holdout points using
    the composed prediction (``predicted``). These values are identical to
    the headline ``directional_pnl`` / ``sharpe_ratio`` / ``hit_rate`` /
    ``max_drawdown`` in the top-level response.

    ``rule_layer`` — trading metrics computed over ALL holdout points using
    the symbolic rule-layer-only prediction (``rule_layer_predicted``).

    ``neural`` — trading metrics computed over ALL holdout points using the
    GBT baseline prediction (``neural``). Present when
    ``baseline_mode='neural'`` (the default).

    This lets a consumer reconcile the headline trading metrics with the
    per-point fitted series: ``per_tier_skill['composed']`` equals the
    headline, ``per_tier_skill['rule_layer']`` shows the symbolic rules'
    standalone trading performance, and ``per_tier_skill['neural']`` shows
    the GBT baseline's standalone trading performance."""

    forecast: Required[ForecastBlock]
    why: Required[list[JsonDict]]
    prediction_record: Required[PredictionRecord]
    target_field: str
    horizon: int
    baseline: float
    skill_vs_persistence: float
    backtest_skill_vs_persistence: float
    max_standalone_holdout_skill: float
    drivers_fired: int
    point_is_persistence: bool
    accepted_drivers: list[JsonDict]
    mode: str
    hit_rate_alpha: float
    sign_base_rate: float
    neural_model_name: str | None
    neural_holdout_skill: float | None
    prediction_react_trajectory: JsonDict | None
    prediction_screen_enabled: bool
    why_certification: JsonDict
    fitted_series: JsonDict
    unmatched_overrides: list[str]
    discovery_mode: bool
    driver_report: list[JsonDict]


class DriverReportEntry(TypedDict, total=False):
    """One ranked driver in a :class:`FindDriversResult` ``driver_report``.

    Each entry is an aggregated base-series driver enriched with holdout
    evidence. ``holdout_skill`` is the MAX standalone holdout skill among
    contributing driver-rules; ``significance`` is the MAX fire-rate."""

    series: Required[str]
    label: Required[str]
    description: str
    known: bool
    importance: float
    importance_share: float
    strength: str  # "strong" | "moderate" | "weak"
    driver_count: int
    fired_on_latest_row: bool
    holdout_skill: float | None
    significance: float | None
    provenance: str  # "discovered" | "supplied"


class FindDriversResult(TypedDict, total=False):
    """What ``find_drivers`` returns -- a :class:`SymbolicForecastResult` with
    ``discovery_mode=True`` and a ``driver_report`` (the ranked drivers with
    their holdout evidence). The full ``why`` / ``forecast`` /
    ``prediction_record`` are still present for consumers that need them."""

    discovery_mode: Required[bool]
    driver_report: Required[list[DriverReportEntry]]
    forecast: Required[ForecastBlock]
    why: Required[list[JsonDict]]
    prediction_record: Required[PredictionRecord]
    target_field: str
    horizon: int
    baseline: float
    skill_vs_persistence: float
    backtest_skill_vs_persistence: float
    rule_layer_marginal: float | None
    max_standalone_holdout_skill: float
    drivers_fired: int
    point_is_persistence: bool
    accepted_drivers: list[JsonDict]
    aggregated_drivers: list[JsonDict]
    mode: str


class PredictionBlock(TypedDict, total=False):
    """The ``prediction`` sub-object of a :class:`PredictResult`.

    Since 1.0.0 ``value`` is LEVEL space by default for a differenced target and
    the change is exposed alongside as ``value_change`` (``value_space ==
    "level"``); on the no-history path ``value`` stays the raw change and
    ``value_space == "transformed_unreconstructed"`` (treat as unreliable). This
    is documented as an OPEN block server-side (it may carry additional keys), so
    treat these fields as the documented subset, not an exhaustive list."""

    value: Required[float]
    value_space: Required[str]  # "level" | "transformed_unreconstructed"
    value_change: float | None
    target_transform: str | None
    baseline: float | None
    lower_bound: float | None
    upper_bound: float | None
    raw_value: float | None


class PredictResult(TypedDict, total=False):
    """What ``predictions.predict`` returns. ``prediction`` is the point forecast
    (:class:`PredictionBlock`); ``explanation`` (with ``explain=True``) is an
    OPEN block (``feature_importance`` / ``model`` / rules fired / ``narrative``)
    typed as :data:`JsonDict`."""

    platform_id: Required[int]
    target: Required[str]
    mode: Required[str]  # "timeseries" | "cross_sectional"
    prediction: Required[PredictionBlock]
    horizon: int | None
    frequency: str | None
    explanation: JsonDict
    unmatched_overrides: list[str]


class ResidualDiagnosis(TypedDict, total=False):
    """What ``residual_diagnosis`` returns — a drift-vs-correction hypothesis
    with its evidence."""

    residual: float
    z: float
    breached: bool
    diagnosis: str
    decayed_drivers: list[Any]
    stable_drivers: list[Any]
    evidence: JsonDict
