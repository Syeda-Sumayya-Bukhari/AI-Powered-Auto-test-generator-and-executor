"""Application configuration loaded from environment variables."""

import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# AI provider: mock | openai | gemini | groq | ollama
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").strip().lower()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

BASE_URL = os.getenv("BASE_URL", "https://www.saucedemo.com/").rstrip("/") + "/"

REPORTS_DIR = PROJECT_ROOT / "reports"
GENERATED_TESTS_DIR = PROJECT_ROOT / "generated_tests"

REPORTS_DIR.mkdir(exist_ok=True)
GENERATED_TESTS_DIR.mkdir(exist_ok=True)

DEFAULT_USERNAME = "standard_user"
DEFAULT_PASSWORD = "secret_sauce"

SELENIUM_GRID_URL = os.getenv("SELENIUM_GRID_URL", "").strip()
SELENIUM_GRID_BROWSERS = [
    browser.strip()
    for browser in os.getenv("SELENIUM_GRID_BROWSERS", "chrome,firefox").split(",")
    if browser.strip()
]
SELENIUM_GRID_PLATFORM = os.getenv("SELENIUM_GRID_PLATFORM", "ANY").strip()
