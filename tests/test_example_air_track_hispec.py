"""Offline tests for the high-spec ISR air-track example (``24_air_track_isr_hispec``).

All offline — no API, no network. Adapted from the upstream demo's offline tests:
the ``_triage`` verdict parser, showcase-track well-formedness, reference-policy
correctness of the showcase expected labels, and that the shipped synthetic dataset
loads and is features-only. (Upstream live-feed-parsing tests are intentionally NOT
ported — the shipped example is synthetic-only and ships no live-data client.)
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parents[1] / "examples"
EXAMPLE_PATH = EXAMPLES_DIR / "24_air_track_isr_hispec.py"
DATA_PATH = EXAMPLES_DIR / "data" / "air_tracks_hispec.csv"

# Feature columns the standardised dataset is expected to carry (no label columns).
FEATURE_COLUMNS = {
    "track_number", "icao24", "callsign", "origin_country", "position_source",
    "mode3a_code", "emergency_squawk", "spi", "iff_mode", "flight_plan_correlated",
    "on_ground", "baro_altitude_ft", "geo_altitude_ft", "ground_speed_kts",
    "track_angle_deg", "vertical_rate_fpm", "latitude_deg", "longitude_deg",
    "in_restricted_zone", "corridor_compliant", "origin_known",
    "sensor_platform", "sensor_latitude", "sensor_longitude", "sensor_true_altitude_ft",
    "slant_range_m", "track_confidence",
}
LABEL_COLUMNS = {"decision", "triage_reason"}


def _load_example():
    # The module name starts with a digit, so import it by file path.
    spec = importlib.util.spec_from_file_location("ex24_air_track_isr_hispec", EXAMPLE_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # The example imports ``_common`` (a sibling module); make it importable.
    import sys
    sys.path.insert(0, str(EXAMPLES_DIR))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(EXAMPLES_DIR))
    return module


@pytest.fixture(scope="module")
def demo():
    return _load_example()


def _reference_policy(r: dict) -> str:
    """Mirror of the demo's documented triage policy (first matching rule wins).

    Used only to confirm the showcase's hand-written expected labels are
    self-consistent with the stated policy.
    """
    emergency = bool(r["emergency_squawk"]) or r["iff_mode"] == "emergency"
    identified = bool(r["flight_plan_correlated"]) and r["iff_mode"] == "mode3_valid"
    zone_breach = bool(r["in_restricted_zone"]) and not r["corridor_compliant"]
    fast_low = r["ground_speed_kts"] >= 600 and r["baro_altitude_ft"] <= 2000
    implausible = fast_low or r["vertical_rate_fpm"] >= 8000
    if emergency:
        return "escalate"
    if zone_breach:
        return "escalate"
    if (not identified) and r["iff_mode"] in ("no_response", "mode3_invalid"):
        return "escalate"
    if implausible:
        return "monitor"
    if not identified:
        return "monitor"
    return "clear"


# --- import smoke ------------------------------------------------------------


class TestImport:
    def test_example_imports(self, demo) -> None:
        assert demo.DOMAIN_NAME == "Air Track Triage (High-Spec ISR)"
        assert callable(demo.run_air_track_hispec_demo)
        assert callable(demo._triage)


# --- _triage verdict parser --------------------------------------------------


class TestTriageParsing:
    def test_reads_escalate_verdict(self, demo) -> None:
        report = {"answer": "**Decision: Escalate — zone breach.** more text"}
        assert demo._triage(report)[0] == "escalate"

    def test_reads_monitor_verdict(self, demo) -> None:
        assert demo._triage({"answer": "**Decision: Monitor — origin unknown.**"})[0] == "monitor"

    def test_reads_clear_verdict(self, demo) -> None:
        assert demo._triage({"answer": "**Decision: Clear — nothing applies.**"})[0] == "clear"

    def test_does_not_keyword_match_proof_trace(self, demo) -> None:
        # A Clear decision whose proof text mentions 'escalate' rules must read Clear.
        report = {"answer": "**Decision: Clear — no action.**",
                  "proof_summary": "rules: Escalate for emergency (not fired); Monitor (not)"}
        assert demo._triage(report)[0] == "clear"

    def test_unparseable_defaults_to_clear(self, demo) -> None:
        assert demo._triage({"answer": "no verdict here"})[0] == "clear"


# --- showcase tracks ---------------------------------------------------------


class TestShowcaseTracks:
    def test_all_tracks_carry_every_feature_column(self, demo) -> None:
        for label, _expected, facts in demo.SHOWCASE_TRACKS:
            missing = FEATURE_COLUMNS - set(facts)
            assert not missing, f"track {label!r} missing {missing}"

    def test_tracks_carry_no_label_columns(self, demo) -> None:
        for label, _expected, facts in demo.SHOWCASE_TRACKS:
            leaked = LABEL_COLUMNS & set(facts)
            assert not leaked, f"track {label!r} leaks label column {leaked}"

    def test_expected_levels_are_valid(self, demo) -> None:
        for _label, expected, _facts in demo.SHOWCASE_TRACKS:
            assert expected in {"clear", "monitor", "escalate"}

    def test_expected_labels_match_reference_policy(self, demo) -> None:
        # The hand-written expected verdicts must agree with the stated triage policy.
        for label, expected, facts in demo.SHOWCASE_TRACKS:
            assert _reference_policy(facts) == expected, f"track {label!r} mislabelled"


# --- shipped synthetic dataset ----------------------------------------------


class TestDataset:
    def test_dataset_exists(self) -> None:
        assert DATA_PATH.exists(), f"missing synthetic dataset {DATA_PATH}"

    def test_dataset_is_features_only(self) -> None:
        with DATA_PATH.open(newline="") as f:
            header = next(csv.reader(f))
        cols = set(header)
        assert cols == FEATURE_COLUMNS
        assert not (LABEL_COLUMNS & cols), "shipped dataset must NOT contain label columns"

    def test_dataset_loads_rows(self) -> None:
        with DATA_PATH.open(newline="") as f:
            rows = list(csv.DictReader(f))
        assert len(rows) > 100
        # Spot-check a numeric + an enum field parse sanely.
        first = rows[0]
        assert float(first["track_confidence"]) >= 0.0
        assert first["position_source"] in {
            "ads_b", "asterix_radar", "mlat", "flarm", "fused"}
