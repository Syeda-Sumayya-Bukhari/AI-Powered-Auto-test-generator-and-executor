"""Validate and normalize AI-generated test plans."""

from __future__ import annotations

from typing import Any

ALLOWED_ACTIONS = {
    "navigate",
    "type",
    "click",
    "select",
    "assert_text",
    "assert_url",
    "assert_element",
}


class TestPlanValidationError(ValueError):
    """Raised when generated test plan structure is invalid."""
    __test__ = False


def validate_test_plan(plan: dict[str, Any]) -> dict[str, Any]:
    """Ensure required keys exist and steps use supported actions."""
    if not isinstance(plan, dict):
        raise TestPlanValidationError("Test plan must be a JSON object")

    for key in ("requirement", "application_url", "scenarios", "test_cases"):
        if key not in plan:
            raise TestPlanValidationError(f"Missing required field: {key}")

    if not isinstance(plan["scenarios"], list) or not plan["scenarios"]:
        raise TestPlanValidationError("scenarios must be a non-empty list")

    if not isinstance(plan["test_cases"], list) or not plan["test_cases"]:
        raise TestPlanValidationError("test_cases must be a non-empty list")

    scenario_ids = {s.get("id") for s in plan["scenarios"]}
    for case in plan["test_cases"]:
        if not case.get("id"):
            raise TestPlanValidationError("Each test case must have an id")
        if case.get("scenario_id") not in scenario_ids:
            raise TestPlanValidationError(
                f"Test case {case['id']} references unknown scenario {case.get('scenario_id')}"
            )
        steps = case.get("steps", [])
        if not steps:
            raise TestPlanValidationError(f"Test case {case['id']} has no steps")
        for step in steps:
            action = step.get("action", "")
            if action not in ALLOWED_ACTIONS:
                raise TestPlanValidationError(f"Unsupported action: {action}")

    return plan


def get_test_case_by_id(plan: dict[str, Any], case_id: str) -> dict[str, Any] | None:
    for case in plan.get("test_cases", []):
        if case.get("id") == case_id:
            return case
    return None
