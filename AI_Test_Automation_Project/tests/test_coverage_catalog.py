"""Verify comprehensive positive + negative coverage across all modules."""

from src.mock_test_catalog import MODULES, build_mock_test_plan, get_coverage_matrix


def test_all_four_modules_in_full_suite():
    plan = build_mock_test_plan("full", "https://www.saucedemo.com/", "All Modules")
    assert set(plan["modules_tested"]) == set(MODULES)
    assert plan["summary"]["total_cases"] == 17


def test_each_module_has_positive_and_negative_cases():
    for row in get_coverage_matrix():
        assert row["positive"] >= 1, f"{row['module']} missing positive tests"
        assert row["negative"] >= 1, f"{row['module']} missing negative tests"


def test_full_suite_has_both_test_types():
    plan = build_mock_test_plan("full", "https://www.saucedemo.com/", "All Modules")
    assert plan["summary"]["positive_scenarios"] >= 8
    assert plan["summary"]["negative_scenarios"] >= 6


def test_login_module_filter_keeps_mixed_types():
    plan = build_mock_test_plan("login", "https://www.saucedemo.com/", "Login")
    types = {c.get("test_type") for c in plan["test_cases"]}
    assert types == {"positive", "negative"}
