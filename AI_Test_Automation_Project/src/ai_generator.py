"""Generate structured test cases from natural-language requirements."""

from __future__ import annotations

import json
import re
from typing import Any

from src.ai_providers import call_ai_provider, get_active_provider
from src.config import AI_PROVIDER, BASE_URL

# Re-export for tests and backward compatibility
from src.ai_providers import SYSTEM_PROMPT, build_user_prompt  # noqa: F401


def extract_json(text: str) -> dict[str, Any]:
    """Parse JSON from model response, tolerating optional markdown fences."""
    cleaned = text.strip()
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if fence_match:
        cleaned = fence_match.group(1).strip()
    return json.loads(cleaned)


def generate_mock_test_plan(
    requirement: str,
    base_url: str,
    module_filter: str = "All Modules",
) -> dict[str, Any]:
    """Fallback when AI_PROVIDER=mock or API call fails."""
    from src.mock_test_catalog import build_mock_test_plan as build_catalog

    return build_catalog(requirement, base_url, module_filter)


def generate_test_plan(requirement: str, base_url: str | None = None) -> dict[str, Any]:
    """
    Generate test scenarios and cases from a natural-language requirement.

    Provider is set via AI_PROVIDER in .env: mock | gemini | groq | ollama | openai
    """
    url = base_url or BASE_URL
    provider = get_active_provider()

    if provider == "mock":
        return generate_mock_test_plan(requirement, url)

    try:
        content = call_ai_provider(requirement, url)
        plan = extract_json(content)
        plan.setdefault("requirement", requirement)
        plan.setdefault("application_url", url)
        plan["_ai_provider"] = provider
        return plan
    except Exception as exc:
        print(f"[WARNING] AI provider '{provider}' failed: {exc}")
        print("[WARNING] Falling back to built-in mock test plan.")
        plan = generate_mock_test_plan(requirement, url)
        plan["_ai_provider"] = "mock (fallback)"
        return plan


def provider_label() -> str:
    """Human-readable label for console output."""
    p = get_active_provider()
    if p == "mock":
        return "mock (offline, no API key needed)"
    return p
