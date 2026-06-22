"""Free and paid AI providers for test case generation."""

from __future__ import annotations

import json
from typing import Any

import requests
from openai import OpenAI

from src.config import (
    AI_PROVIDER,
    GEMINI_API_KEY,
    GEMINI_MODEL,
    GROQ_API_KEY,
    GROQ_MODEL,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OPENAI_API_KEY,
    OPENAI_MODEL,
)

SYSTEM_PROMPT = """You are a senior QA automation engineer.
Given a web application URL and a testing requirement, produce test artifacts as JSON only.

Return a single JSON object with this exact structure:
{
  "requirement": "<original requirement>",
  "application_url": "<url>",
  "scenarios": [
    {
      "id": "SC-001",
      "title": "<scenario title>",
      "description": "<brief description>"
    }
  ],
  "test_cases": [
    {
      "id": "TC-001",
      "scenario_id": "SC-001",
      "title": "<test case title>",
      "priority": "High|Medium|Low",
      "preconditions": ["<precondition>"],
      "steps": [
        {"action": "navigate|type|click|assert_text|assert_url|assert_element", "target": "<selector or url path>", "value": "<optional value>", "description": "<human readable step>"}
      ],
      "expected_output": "<expected result>",
      "test_data": {"username": "", "password": ""}
    }
  ]
}

Rules:
- Use CSS selectors valid for Selenium (e.g. #user-name, #password, #login-button).
- For saucedemo.com login: username #user-name, password #password, login #login-button.
- Include positive and at least one negative scenario when relevant.
- steps must be executable by a simple Selenium runner.
- Output JSON only, no markdown fences."""


def build_user_prompt(requirement: str, base_url: str) -> str:
    return (
        f"Application URL: {base_url}\n"
        f"Requirement: {requirement}\n"
        "Generate scenarios and detailed test cases with steps and expected outputs."
    )


def _openai_compatible_chat(
    *,
    api_key: str,
    base_url: str | None,
    model: str,
    requirement: str,
    base_url_app: str,
) -> str:
    kwargs: dict[str, Any] = {"api_key": api_key}
    if base_url:
        kwargs["base_url"] = base_url
    client = OpenAI(**kwargs)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(requirement, base_url_app)},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or ""


def call_openai(requirement: str, base_url: str) -> str:
    if not OPENAI_API_KEY or OPENAI_API_KEY == "your_openai_api_key_here":
        raise ValueError("OPENAI_API_KEY is not set in .env")
    return _openai_compatible_chat(
        api_key=OPENAI_API_KEY,
        base_url=None,
        model=OPENAI_MODEL,
        requirement=requirement,
        base_url_app=base_url,
    )


def call_groq(requirement: str, base_url: str) -> str:
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is not set in .env")
    return _openai_compatible_chat(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
        model=GROQ_MODEL,
        requirement=requirement,
        base_url_app=base_url,
    )


def call_gemini(requirement: str, base_url: str) -> str:
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not set in .env")
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise ImportError(
            "Install Gemini support: pip install google-generativeai"
        ) from exc

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    prompt = f"{SYSTEM_PROMPT}\n\n{build_user_prompt(requirement, base_url)}"
    response = model.generate_content(prompt)
    return response.text or ""


def call_ollama(requirement: str, base_url: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"
    payload = {
        "model": OLLAMA_MODEL,
        "stream": False,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(requirement, base_url)},
        ],
    }
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
    except requests.ConnectionError as exc:
        raise ConnectionError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            "Install Ollama and run: ollama serve"
        ) from exc
    data = response.json()
    return data.get("message", {}).get("content", "")


PROVIDER_HANDLERS = {
    "openai": call_openai,
    "gemini": call_gemini,
    "groq": call_groq,
    "ollama": call_ollama,
}


def get_active_provider() -> str:
    """Resolve which provider will be used."""
    provider = AI_PROVIDER
    if provider == "mock":
        return "mock"
    if provider not in PROVIDER_HANDLERS:
        return "mock"
    return provider


def call_ai_provider(requirement: str, base_url: str) -> str:
    provider = get_active_provider()
    if provider == "mock":
        raise ValueError("Mock provider does not call external APIs")
    handler = PROVIDER_HANDLERS[provider]
    return handler(requirement, base_url)
