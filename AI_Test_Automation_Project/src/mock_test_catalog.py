"""
Comprehensive mock test catalog — 4 modules, mixed PASS/FAIL outcomes.

Sauce Demo: https://www.saucedemo.com/
"""

from __future__ import annotations

from typing import Any

MODULES = ("Login", "Inventory", "Cart", "Checkout")


def _step(action: str, target: str, value: str = "", description: str = "") -> dict[str, str]:
    return {
        "action": action,
        "target": target,
        "value": value,
        "description": description or action,
    }


def _login(user: str = "standard_user", password: str = "secret_sauce") -> list[dict[str, str]]:
    return [
        _step("navigate", "/", description="Open login page"),
        _step("type", "#user-name", user, "Enter username"),
        _step("type", "#password", password, "Enter password"),
        _step("click", "#login-button", description="Click Login"),
    ]


def _login_inventory() -> list[dict[str, str]]:
    return _login() + [_step("assert_url", "inventory.html", description="Verify inventory page")]


def _add_backpack_to_cart() -> list[dict[str, str]]:
    return [_step("click", "#add-to-cart-sauce-labs-backpack", description="Add backpack to cart")]


def _all_scenarios() -> list[dict[str, Any]]:
    return [
        {"id": "SC-L01", "module": "Login", "title": "Valid authentication", "description": "Successful login flows"},
        {"id": "SC-L02", "module": "Login", "title": "Invalid authentication", "description": "Rejected login attempts"},
        {"id": "SC-I01", "module": "Inventory", "title": "Product catalog", "description": "Inventory listing and content"},
        {"id": "SC-I02", "module": "Inventory", "title": "Inventory sorting", "description": "Sort products on inventory page"},
        {"id": "SC-C01", "module": "Cart", "title": "Add to cart", "description": "Adding products to shopping cart"},
        {"id": "SC-C02", "module": "Cart", "title": "Cart validation", "description": "Cart badge and cart page checks"},
        {"id": "SC-K01", "module": "Checkout", "title": "Checkout happy path", "description": "Complete purchase flow"},
        {"id": "SC-K02", "module": "Checkout", "title": "Checkout verification", "description": "Post-checkout assertions"},
    ]


def _all_test_cases() -> list[dict[str, Any]]:
    return [
        # ─── LOGIN (5 cases: 4 PASS, 1 FAIL) ─────────────────────────────────
        {
            "id": "TC-L01",
            "module": "Login",
            "scenario_id": "SC-L01",
            "title": "Login with valid credentials",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User on login page"],
            "steps": _login() + [_step("assert_url", "inventory.html", description="Redirect to inventory")],
            "expected_output": "User reaches inventory page",
        },
        {
            "id": "TC-L02",
            "module": "Login",
            "scenario_id": "SC-L02",
            "title": "Login with invalid password",
            "priority": "High",
            "test_type": "negative",
            "expected_result": "PASS",
            "preconditions": ["User on login page"],
            "steps": _login(password="wrong_pass") + [
                _step("assert_element", "[data-test='error']", description="Error message shown")
            ],
            "expected_output": "Login error displayed",
        },
        {
            "id": "TC-L03",
            "module": "Login",
            "scenario_id": "SC-L02",
            "title": "Login with locked out user",
            "priority": "Medium",
            "test_type": "negative",
            "expected_result": "PASS",
            "preconditions": ["User on login page"],
            "steps": _login(user="locked_out_user") + [
                _step("assert_element", "[data-test='error']", description="Locked out error shown")
            ],
            "expected_output": "Account locked message displayed",
        },
        {
            "id": "TC-L04",
            "module": "Login",
            "scenario_id": "SC-L02",
            "title": "Login with empty username",
            "priority": "Medium",
            "test_type": "negative",
            "expected_result": "PASS",
            "preconditions": ["User on login page"],
            "steps": [
                _step("navigate", "/", description="Open login page"),
                _step("type", "#password", "secret_sauce", "Enter password only"),
                _step("click", "#login-button", description="Click Login"),
                _step("assert_element", "[data-test='error']", description="Validation error shown"),
            ],
            "expected_output": "Username required error displayed",
        },
        {
            "id": "TC-L05",
            "module": "Login",
            "scenario_id": "SC-L01",
            "title": "Login redirect to wrong page (negative)",
            "priority": "Low",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User on login page"],
            "steps": _login() + [
                _step("assert_url", "admin-dashboard.html", description="Expect wrong URL (should fail)")
            ],
            "expected_output": "Should fail — incorrect expected URL",
        },
        # ─── INVENTORY (4 cases: 3 PASS, 1 FAIL) ─────────────────────────────
        {
            "id": "TC-I01",
            "module": "Inventory",
            "scenario_id": "SC-I01",
            "title": "Inventory page displays product list",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + [
                _step("assert_element", ".inventory_list", description="Product list visible")
            ],
            "expected_output": "Inventory list is displayed",
        },
        {
            "id": "TC-I02",
            "module": "Inventory",
            "scenario_id": "SC-I01",
            "title": "Verify Sauce Labs Backpack product name",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + [
                _step(
                    "assert_text",
                    ".inventory_item_name",
                    "Sauce Labs Backpack",
                    "Backpack name visible",
                )
            ],
            "expected_output": "Backpack product title is shown",
        },
        {
            "id": "TC-I03",
            "module": "Inventory",
            "scenario_id": "SC-I01",
            "title": "Verify non-existent product (negative)",
            "priority": "Medium",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + [
                _step(
                    "assert_text",
                    ".inventory_item_name",
                    "Ultra Premium Fake Product",
                    "Fake product should not exist",
                )
            ],
            "expected_output": "Should fail — product does not exist",
        },
        {
            "id": "TC-I04",
            "module": "Inventory",
            "scenario_id": "SC-I02",
            "title": "Sort products price low to high",
            "priority": "Medium",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + [
                _step("select", ".product_sort_container", "lohi", "Sort price low to high"),
                _step("assert_element", ".inventory_list", description="List still visible after sort"),
            ],
            "expected_output": "Products remain listed after sorting",
        },
        # ─── CART (4 cases: 3 PASS, 1 FAIL) ──────────────────────────────────
        {
            "id": "TC-C01",
            "module": "Cart",
            "scenario_id": "SC-C01",
            "title": "Add backpack to cart",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + _add_backpack_to_cart() + [
                _step("assert_element", ".shopping_cart_link", description="Cart link available")
            ],
            "expected_output": "Item added without error",
        },
        {
            "id": "TC-C02",
            "module": "Cart",
            "scenario_id": "SC-C02",
            "title": "Cart badge shows 1 item",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + _add_backpack_to_cart() + [
                _step("assert_text", ".shopping_cart_badge", "1", "Badge shows one item")
            ],
            "expected_output": "Cart badge displays 1",
        },
        {
            "id": "TC-C03",
            "module": "Cart",
            "scenario_id": "SC-C02",
            "title": "Cart badge shows 99 items (negative)",
            "priority": "Low",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User logged in"],
            "steps": _login_inventory() + _add_backpack_to_cart() + [
                _step("assert_text", ".shopping_cart_badge", "99", "Wrong badge count")
            ],
            "expected_output": "Should fail — only one item in cart",
        },
        {
            "id": "TC-C04",
            "module": "Cart",
            "scenario_id": "SC-C01",
            "title": "Open cart page with item listed",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in", "Item in cart"],
            "steps": _login_inventory() + _add_backpack_to_cart() + [
                _step("click", ".shopping_cart_link", description="Open cart"),
                _step("assert_element", ".cart_item", description="Cart item row visible"),
            ],
            "expected_output": "Cart page lists added product",
        },
        # ─── CHECKOUT (4 cases: 2 PASS, 2 FAIL) ──────────────────────────────
        {
            "id": "TC-K01",
            "module": "Checkout",
            "scenario_id": "SC-K01",
            "title": "Complete checkout with valid details",
            "priority": "High",
            "test_type": "positive",
            "expected_result": "PASS",
            "preconditions": ["User logged in", "Item in cart"],
            "steps": _login_inventory()
            + _add_backpack_to_cart()
            + [
                _step("click", ".shopping_cart_link", description="Open cart"),
                _step("click", "#checkout", description="Start checkout"),
                _step("type", "#first-name", "Sara", "Enter first name"),
                _step("type", "#last-name", "Khan", "Enter last name"),
                _step("type", "#postal-code", "44000", "Enter postal code"),
                _step("click", "#continue", description="Continue to overview"),
                _step("click", "#finish", description="Finish order"),
                _step("assert_element", ".complete-header", description="Order complete header"),
            ],
            "expected_output": "Thank you page displayed",
        },
        {
            "id": "TC-K02",
            "module": "Checkout",
            "scenario_id": "SC-K02",
            "title": "Checkout without filling customer info (negative)",
            "priority": "Medium",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User logged in", "Item in cart"],
            "steps": _login_inventory()
            + _add_backpack_to_cart()
            + [
                _step("click", ".shopping_cart_link", description="Open cart"),
                _step("click", "#checkout", description="Start checkout"),
                _step("click", "#continue", description="Continue without filling form"),
                _step("assert_element", "#finish", description="Finish should not be available yet"),
            ],
            "expected_output": "Should fail — form validation blocks continue",
        },
        {
            "id": "TC-K03",
            "module": "Checkout",
            "scenario_id": "SC-K02",
            "title": "Wrong order confirmation message (negative)",
            "priority": "Low",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User logged in", "Item in cart"],
            "steps": _login_inventory()
            + _add_backpack_to_cart()
            + [
                _step("click", ".shopping_cart_link", description="Open cart"),
                _step("click", "#checkout", description="Start checkout"),
                _step("type", "#first-name", "Ali", "Enter first name"),
                _step("type", "#last-name", "Raza", "Enter last name"),
                _step("type", "#postal-code", "54000", "Enter postal code"),
                _step("click", "#continue", description="Continue"),
                _step("click", "#finish", description="Finish order"),
                _step(
                    "assert_text",
                    ".complete-header",
                    "Payment Declined",
                    "Wrong confirmation text",
                ),
            ],
            "expected_output": "Should fail — actual message is Thank you",
        },
        {
            "id": "TC-K04",
            "module": "Checkout",
            "scenario_id": "SC-K01",
            "title": "Open empty cart checkout (negative)",
            "priority": "Medium",
            "test_type": "negative",
            "expected_result": "FAIL",
            "preconditions": ["User logged in", "Empty cart"],
            "steps": _login_inventory()
            + [
                _step("click", ".shopping_cart_link", description="Open empty cart"),
                _step("assert_element", ".cart_item", description="Expect cart item but cart is empty"),
            ],
            "expected_output": "Should fail — no items in cart",
        },
    ]


def _infer_module_filter(requirement: str) -> str:
    lower = requirement.lower()
    if any(keyword in lower for keyword in ["checkout", "customer", "order", "billing", "payment", "finish", "postal code"]):
        return "Checkout"
    if any(keyword in lower for keyword in ["cart", "shopping cart", "badge", "add to cart", "checkout page"]):
        return "Cart"
    if any(keyword in lower for keyword in ["inventory", "product list", "products", "sort"]):
        return "Inventory"
    if any(keyword in lower for keyword in ["login", "sign in", "credentials", "username", "password", "error message"]):
        return "Login"
    return "All Modules"


def build_mock_test_plan(
    requirement: str,
    base_url: str,
    module_filter: str = "All Modules",
) -> dict[str, Any]:
    """Build plan with optional filter by module name."""
    scenarios = _all_scenarios()
    cases = _all_test_cases()

    inferred_filter = module_filter
    if module_filter == "Custom":
        inferred_filter = _infer_module_filter(requirement)

    if inferred_filter and inferred_filter not in ("All Modules", ""):
        cases = [c for c in cases if c.get("module") == inferred_filter]
        scenario_ids = {c["scenario_id"] for c in cases}
        scenarios = [s for s in scenarios if s["id"] in scenario_ids]

    # Strip internal expected_result from exported case copy
    export_cases = []
    for case in cases:
        copy = {k: v for k, v in case.items() if k != "expected_result"}
        export_cases.append(copy)

    result = {
        "requirement": requirement,
        "application_url": base_url,
        "module_filter": module_filter,
        "modules_tested": list({c.get("module") for c in cases}),
        "scenarios": scenarios,
        "test_cases": export_cases,
        "summary": {
            "total_cases": len(cases),
            "expected_pass": sum(1 for c in cases if c.get("expected_result") == "PASS"),
            "expected_fail": sum(1 for c in cases if c.get("expected_result") == "FAIL"),
            "positive_scenarios": sum(1 for c in cases if c.get("test_type") == "positive"),
            "negative_scenarios": sum(1 for c in cases if c.get("test_type") == "negative"),
        },
    }
    return result


def get_coverage_matrix() -> list[dict[str, Any]]:
    """Return per-module positive/negative coverage for reports and unit tests."""
    cases = _all_test_cases()
    matrix: list[dict[str, Any]] = []
    for module in MODULES:
        module_cases = [c for c in cases if c.get("module") == module]
        positive = [c for c in module_cases if c.get("test_type") == "positive"]
        negative = [c for c in module_cases if c.get("test_type") == "negative"]
        matrix.append(
            {
                "module": module,
                "total": len(module_cases),
                "positive": len(positive),
                "negative": len(negative),
                "positive_ids": [c["id"] for c in positive],
                "negative_ids": [c["id"] for c in negative],
            }
        )
    return matrix
