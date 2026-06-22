"""Unit tests for test plan validation (Task 2 — pyunit/pytest)."""

import pytest

from src.ai_generator import generate_mock_test_plan
from src.test_parser import TestPlanValidationError, get_test_case_by_id, validate_test_plan


@pytest.fixture
def valid_plan():
    return generate_mock_test_plan("Test login page", "https://www.saucedemo.com/")


def test_validate_accepts_valid_plan(valid_plan):
    result = validate_test_plan(valid_plan)
    assert result["requirement"] == "Test login page"
    assert len(result["test_cases"]) >= 2


def test_validate_rejects_missing_scenarios(valid_plan):
    plan = dict(valid_plan)
    del plan["scenarios"]
    with pytest.raises(TestPlanValidationError, match="scenarios"):
        validate_test_plan(plan)


def test_validate_rejects_empty_test_cases(valid_plan):
    plan = dict(valid_plan)
    plan["test_cases"] = []
    with pytest.raises(TestPlanValidationError, match="test_cases"):
        validate_test_plan(plan)


def test_validate_rejects_unknown_scenario_id(valid_plan):
    plan = dict(valid_plan)
    plan["test_cases"][0]["scenario_id"] = "SC-999"
    with pytest.raises(TestPlanValidationError, match="unknown scenario"):
        validate_test_plan(plan)


def test_validate_rejects_invalid_action(valid_plan):
    plan = dict(valid_plan)
    plan["test_cases"][0]["steps"][0]["action"] = "fly_to_moon"
    with pytest.raises(TestPlanValidationError, match="Unsupported action"):
        validate_test_plan(plan)


def test_get_test_case_by_id(valid_plan):
    case = get_test_case_by_id(valid_plan, "TC-L01")
    assert case is not None
    assert "valid credentials" in case["title"].lower()


def test_get_test_case_by_id_not_found(valid_plan):
    assert get_test_case_by_id(valid_plan, "TC-999") is None


def test_validate_rejects_missing_test_case_id(valid_plan):
    plan = dict(valid_plan)
    del plan["test_cases"][0]["id"]
    with pytest.raises(TestPlanValidationError, match="must have an id"):
        validate_test_plan(plan)


def test_validate_rejects_empty_steps(valid_plan):
    plan = dict(valid_plan)
    plan["test_cases"][0]["steps"] = []
    with pytest.raises(TestPlanValidationError, match="has no steps"):
        validate_test_plan(plan)
