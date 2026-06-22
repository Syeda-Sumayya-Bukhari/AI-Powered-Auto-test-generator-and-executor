"""Unit tests for pipeline helpers."""

from src.pipeline import build_requirement, MODULE_PRESETS


def test_build_requirement_login_module():
    text = build_requirement("Login", "Check error message for wrong password")
    assert "login" in text.lower()
    assert "wrong password" in text.lower()


def test_build_requirement_custom_only():
    text = build_requirement("Custom", "Test add to cart flow")
    assert text == "Test add to cart flow"


def test_module_presets_not_empty():
    assert MODULE_PRESETS["Login"]
    assert MODULE_PRESETS["Cart"] == "" or "cart" in MODULE_PRESETS["Cart"].lower()


def test_login_module_filter_has_fewer_cases():
    from src.mock_test_catalog import build_mock_test_plan

    full = build_mock_test_plan("req", "https://www.saucedemo.com/", "All Modules")
    login_only = build_mock_test_plan("req", "https://www.saucedemo.com/", "Login")
    assert len(full["test_cases"]) > len(login_only["test_cases"])
    assert all(c["module"] == "Login" for c in login_only["test_cases"])


def test_custom_requirement_infers_checkout_module():
    from src.mock_test_catalog import build_mock_test_plan

    plan = build_mock_test_plan(
        "Test the checkout module: fill customer information, review order summary, and complete checkout flow.",
        "https://www.saucedemo.com/",
        "Custom",
    )
    assert plan["module_filter"] == "Custom"
    assert all(c["module"] == "Checkout" for c in plan["test_cases"])
