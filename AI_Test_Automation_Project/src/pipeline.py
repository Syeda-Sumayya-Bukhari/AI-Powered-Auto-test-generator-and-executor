"""Shared generate / execute pipeline for CLI and web UI."""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from src.ai_generator import extract_json, generate_mock_test_plan
from src.ai_providers import PROVIDER_HANDLERS
from src.config import BASE_URL, GENERATED_TESTS_DIR
from src.report_generator import build_report_payload, save_html_report, save_json_report
from src.selenium_runner import TestCaseResult, run_test_plan, run_test_plan_parallel
from src.test_parser import validate_test_plan

MODULE_PRESETS: dict[str, str] = {
    "All Modules": "Run full regression across Login, Inventory, Cart, and Checkout modules on Sauce Demo.",
    "Login": "Test the login module with valid and invalid credentials, error messages, and redirect to inventory.",
    "Inventory": "Test the inventory module: product list is displayed after login, items are visible, and sorting works.",
    "Cart": "Test the cart module: add item to cart, cart badge updates, and cart page shows added products.",
    "Checkout": "Test the checkout module: fill customer information, review order summary, and complete checkout flow.",
    "Custom": "",
}


def build_requirement(module: str, custom_requirement: str) -> str:
    """Combine module preset with user requirement text."""
    preset = MODULE_PRESETS.get(module, "")
    custom = custom_requirement.strip()
    if module == "Custom":
        return custom or "Test the web application"
    if custom and preset:
        return f"{preset}\n\nAdditional requirement: {custom}"
    return custom or preset


def generate_plan(
    requirement: str,
    *,
    ai_provider: str = "mock",
    base_url: str | None = None,
    module_filter: str = "All Modules",
) -> dict[str, Any]:
    """Generate and validate a test plan."""
    url = base_url or BASE_URL
    provider = ai_provider.strip().lower()

    if provider == "mock":
        plan = generate_mock_test_plan(requirement, url, module_filter=module_filter)
        plan["_ai_provider"] = "mock"
    elif provider in PROVIDER_HANDLERS:
        try:
            handler = PROVIDER_HANDLERS[provider]
            content = handler(requirement, url)
            plan = extract_json(content)
            plan.setdefault("requirement", requirement)
            plan.setdefault("application_url", url)
            plan["_ai_provider"] = provider
        except Exception as exc:
            plan = generate_mock_test_plan(requirement, url, module_filter=module_filter)
            plan["_ai_provider"] = f"mock (fallback: {exc})"
    else:
        plan = generate_mock_test_plan(requirement, url, module_filter=module_filter)
        plan["_ai_provider"] = "mock"

    plan = validate_test_plan(plan)
    plan_path = GENERATED_TESTS_DIR / "latest_test_plan.json"
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    return plan


def execute_plan(
    plan: dict[str, Any],
    *,
    headless: bool = True,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> tuple[list[TestCaseResult], dict[str, Any], Path, Path]:
    """Run Selenium tests and save reports."""
    requirement = plan.get("requirement", "Test run")
    results = run_test_plan(plan, headless=headless, on_progress=on_progress)
    payload = build_report_payload(requirement, results)
    json_path = save_json_report(payload)
    html_path = save_html_report(requirement, results)
    return results, payload, json_path, html_path


def execute_plan_parallel(
    plan: dict[str, Any],
    browser_configs: list[dict[str, Any]],
    *,
    headless: bool = True,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> tuple[list[TestCaseResult], dict[str, Any], Path, Path]:
    requirement = plan.get("requirement", "Test run")
    results = run_test_plan_parallel(plan, browser_configs, headless=headless, on_progress=on_progress)
    payload = build_report_payload(requirement, results)
    json_path = save_json_report(payload)
    html_path = save_html_report(requirement, results)
    return results, payload, json_path, html_path
