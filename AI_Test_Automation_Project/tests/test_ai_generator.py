"""Unit tests for AI test plan generation."""

import json

import pytest

from src.ai_generator import build_user_prompt, extract_json, generate_mock_test_plan, generate_test_plan


def test_mock_plan_has_four_modules_and_mixed_cases():
    plan = generate_mock_test_plan("Full test", "https://www.saucedemo.com/", "All Modules")
    assert len(plan["test_cases"]) >= 16
    modules = {c.get("module") for c in plan["test_cases"]}
    assert modules == {"Login", "Inventory", "Cart", "Checkout"}
    assert plan["summary"]["expected_fail"] >= 4
    assert plan["summary"]["expected_pass"] >= 4


def test_build_user_prompt_includes_requirement():
    prompt = build_user_prompt("Test checkout", "https://example.com/")
    assert "Test checkout" in prompt
    assert "https://example.com/" in prompt


def test_extract_json_plain():
    data = {"a": 1}
    assert extract_json(json.dumps(data)) == data


def test_extract_json_with_markdown_fence():
    raw = '```json\n{"id": "TC-001"}\n```'
    assert extract_json(raw)["id"] == "TC-001"


def test_generate_test_plan_uses_mock_without_api_key(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    monkeypatch.setenv("OPENAI_API_KEY", "")
    plan = generate_test_plan("Test login page")
    assert plan["requirement"] == "Test login page"
    assert "test_cases" in plan


def test_get_active_provider_mock(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "mock")
    from importlib import reload

    import src.config as config
    import src.ai_providers as providers

    reload(config)
    reload(providers)
    assert providers.get_active_provider() == "mock"
