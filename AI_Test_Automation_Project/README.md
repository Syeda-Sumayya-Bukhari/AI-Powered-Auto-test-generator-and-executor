# AI-Powered Test Case Generator + Auto Execution

**SE4343 – Automated Software Testing | Assignment 3 | Spring 2026**  
Capital University of Science and Technology — Department of Software Engineering

## Overview

This project is the **first sprint** toward a semester-long test automation solution. It combines:

1. **AI (OpenAI / ChatGPT)** — generates test scenarios, test cases, steps, and expected outputs from plain English requirements  
2. **Selenium WebDriver** — executes generated tests in a real browser  
3. **Reporting** — HTML and JSON Pass/Fail reports  

**Example:** User enters `"Test login page"` → AI produces structured test cases → Selenium runs them → report is saved under `reports/`.

## Task 1 — Selected Web Application

| Item | Detail |
|------|--------|
| **Application** | [Sauce Demo](https://www.saucedemo.com/) (Swag Labs) |
| **Type** | Public e-commerce demo (industry-standard practice app) |
| **URL** | https://www.saucedemo.com/ |

### Functionalities tested

- User login (valid / invalid credentials)
- Product inventory display
- Add to cart (extendable in later sprints)
- Checkout flow (future sprint)

Demo credentials: `standard_user` / `secret_sauce`

## Architecture

```
User Requirement  →  AI Generator (OpenAI)  →  JSON Test Plan
                                                    ↓
                                            Test Parser (validate)
                                                    ↓
                                            Selenium Runner
                                                    ↓
                                            HTML + JSON Report
```

## Prerequisites

- Python 3.10+
- Google Chrome browser
- AI provider (optional — **mock** works offline with no API key)
- Free alternatives: **Gemini**, **Groq**, or **Ollama** — see [docs/AI_PROVIDERS_SETUP.md](docs/AI_PROVIDERS_SETUP.md)

## Setup

```bash
cd AI_Test_Automation_Project
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # Set AI_PROVIDER=mock|gemini|groq|ollama
```

## Desktop UI (recommended for demo)
 .venv\Scripts\python -u ui_app.py
```bash


Opens a window where you can:
- Select **module** (Login, Inventory, Cart, Checkout, Custom)
- Enter **requirement** text
- Choose **AI provider** (mock = free, no key)
- Click **Generate test cases** | **Execute tests** | **Generate & Execute**

Optional web UI (if Streamlit installs on your Python version):
```bash
pip install streamlit
streamlit run ui_web.py
```

## GUI Testing and Selenium Grid

This project now includes support for Selenium Grid / remote WebDriver execution for parallel browser testing.

Example Grid run:
```bash
python main.py "Test login page" --grid-url http://localhost:4444/wd/hub --grid-browsers chrome,firefox
```

If you do not have a grid hub available, run locally as before.

## CLI Usage

```bash
# Full pipeline: generate + run + report
python main.py "Test login page"

# Show browser while running
python main.py "Test login page" --visible

# Only generate test cases (no browser)
python main.py "Test login page" --generate-only
```

## Task 2 — Unit Testing (pytest)

Unit tests cover **critical framework components** (not the external demo site):

| Module | Tests |
|--------|--------|
| `test_parser.py` | Validation, positive/negative plan structure |
| `test_ai_generator.py` | Mock generation, JSON extraction |
| `test_report_generator.py` | Pass/Fail summary calculations |
| `test_selenium_runner.py` | URL resolution, fail-fast execution (mocked) |

```bash
pytest
```

## Output

- `generated_tests/latest_test_plan.json` — AI-generated scenarios and cases  
- `reports/report_*.html` — visual Pass/Fail report  
- `reports/report_*.json` — machine-readable results  

## GUI Testing Artifacts

Recorded Selenium IDE/Katalon evidence and Task 4 documentation are available in `docs/gui_testing/` and `docs/TASK4_GUI_TESTING.md`.

## Project Structure

```
AI_Test_Automation_Project/
├── main.py
├── requirements.txt
├── src/
│   ├── ai_generator.py
│   ├── test_parser.py
│   ├── selenium_runner.py
│   └── report_generator.py
├── tests/                 # Unit tests (pytest)
├── docs/
│   └── ASSIGNMENT_REPORT.md
└── reports/
```

## References

See [docs/REFERENCES.md](docs/REFERENCES.md) for cited online sources.

## Group / Semester Project Alignment

This sprint establishes the **AI + Selenium + Reporting** foundation. Later sprints will add JMeter performance tests, expanded GUI coverage (Cypress optional), and CI integration per course project requirements.
