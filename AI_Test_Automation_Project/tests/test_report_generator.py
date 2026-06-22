"""Unit tests for report generation."""

from src.report_generator import build_report_payload, results_to_dict
from src.selenium_runner import StepResult, TestCaseResult


def _sample_results():
    return [
        TestCaseResult(
            test_id="TC-001",
            title="Valid login",
            expected_output="Inventory page",
            status="PASS",
            duration_seconds=2.5,
            steps=[StepResult(1, "click", "Click login", "PASS")],
        ),
        TestCaseResult(
            test_id="TC-002",
            title="Invalid login",
            expected_output="Error shown",
            status="FAIL",
            duration_seconds=1.2,
            steps=[StepResult(1, "click", "Click login", "FAIL", "Element not found")],
            error="Element not found",
        ),
    ]


def test_build_report_payload_summary():
    payload = build_report_payload("Test login page", _sample_results())
    assert payload["summary"]["total"] == 2
    assert payload["summary"]["passed"] == 1
    assert payload["summary"]["failed"] == 1
    assert payload["summary"]["pass_rate"] == 50.0


def test_results_to_dict_includes_steps():
    data = results_to_dict(_sample_results())
    assert data[0]["status"] == "PASS"
    assert len(data[1]["steps"]) == 1
    assert data[1]["steps"][0]["message"] == "Element not found"
