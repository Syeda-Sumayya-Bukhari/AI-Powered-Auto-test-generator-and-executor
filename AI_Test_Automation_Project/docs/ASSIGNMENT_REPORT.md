# SE4343 Assignment 3 — Sprint Report

**Course:** SE4343 – Automated Software Testing  
**Institution:** Capital University of Science and Technology  
**Department:** Software Engineering  
**Semester:** Spring 2026  
**Instructor:** Syeda Hafsa Ali (S1, S3)

---

## Task 1: Project Selection (1 point)

### Selected application: Sauce Demo (Swag Labs)

**URL:** https://www.saucedemo.com/

**Description:** Sauce Demo is a publicly available e-commerce demonstration application widely used in the software testing industry for learning Selenium, Cypress, and test automation. It simulates an online store (“Swag Labs”) where users authenticate, browse products, manage a shopping cart, and complete checkout.

**Key functionalities (4 modules under test):**

| Module | Description | Test cases (mock suite) |
|--------|-------------|-------------------------|
| Login | Valid/invalid login, locked user, empty username | 5 (4 PASS, 1 FAIL) |
| Inventory | Product list, product name, sorting | 4 (3 PASS, 1 FAIL) |
| Cart | Add to cart, badge, cart page | 4 (3 PASS, 1 FAIL) |
| Checkout | Full checkout, validation negatives | 4 (2 PASS, 2 FAIL) |

**Full regression:** 17 test cases — mixed Pass/Fail (~65% pass rate), not 100%.

**Why this application:** Stable, free, no local deployment required, and aligns with industry practice for GUI automation training.

---

## Sprint Deliverable: AI Test Generator + Auto Execution

### Workflow

1. Tester provides a requirement in natural language (e.g., “Test login page”).
2. **AI module** (`src/ai_generator.py`) calls OpenAI Chat Completions API (or mock mode) to produce:
   - Test scenarios  
   - Test cases with steps  
   - Expected outputs  
3. **Parser** (`src/test_parser.py`) validates structure and supported Selenium actions.
4. **Selenium runner** (`src/selenium_runner.py`) executes steps in Chrome.
5. **Reporter** (`src/report_generator.py`) writes HTML and JSON reports with Pass/Fail summary.

### Tools used

| Layer | Tool |
|-------|------|
| AI generation | OpenAI API (ChatGPT-compatible models) |
| GUI automation | Selenium WebDriver 4 + Chrome |
| Language | Python 3 |
| Unit testing | pytest |
| Reporting | Jinja2 HTML + JSON |

---

## Comprehensive coverage — positive & negative scenarios

See full matrix: [TEST_COVERAGE.md](TEST_COVERAGE.md)

### Integration tests (Selenium — Sauce Demo)

| Module | Positive cases | Negative cases |
|--------|----------------|----------------|
| Login | TC-L01 | TC-L02, TC-L03, TC-L04, TC-L05 |
| Inventory | TC-I01, TC-I02, TC-I04 | TC-I03 |
| Cart | TC-C01, TC-C02, TC-C04 | TC-C03 |
| Checkout | TC-K01 | TC-K02, TC-K03, TC-K04 |

**Total:** 17 cases — **9 positive**, **8 negative** (mixed Pass/Fail at runtime).

### Unit tests (pytest — framework code)

| Type | Examples |
|------|----------|
| **Positive** | `test_validate_accepts_valid_plan`, `test_build_report_payload_summary` |
| **Negative** | `test_validate_rejects_invalid_action`, `test_validate_rejects_empty_steps`, `test_validate_rejects_missing_test_case_id` |
| **Coverage guard** | `test_each_module_has_positive_and_negative_cases` |

---

## Task 2: Unit Testing (2.5 points)

### Scope

Unit tests target **critical components of the automation framework**. GUI/integration coverage is documented above and executed via Selenium.

### Components tested

| Component | File | Positive tests | Negative tests |
|-----------|------|------------------|----------------|
| Test plan validator | `test_parser.py` | Valid plan accepted | Missing fields, invalid action, empty steps |
| AI generator | `test_ai_generator.py` | Mock plan, JSON parse | — |
| Coverage catalog | `test_coverage_catalog.py` | 4 modules, +/− per module | — |
| Report builder | `test_report_generator.py` | Summary counts | FAIL rows in report |
| Selenium runner | `test_selenium_runner.py` | URL, navigate | Fail-fast |
| Pipeline | `test_pipeline.py` | Requirement build | Module filter |

### How to run

```bash
pytest -v
```

**Insert screenshot:** Terminal output of `pytest -v` here before submission.

---

## Task 4: GUI Testing (Selenium)

### Overview

This sprint adds a dedicated GUI-testing deliverable for Sauce Demo using Selenium WebDriver. The framework now supports:
- automated browser-based test scenarios for navigation, login, cart workflow, checkout and validation
- parallel browser execution using Selenium Grid / remote WebDriver
- recorded evidence from Selenium IDE and Katalon Recorder

### Selenium Grid and parallel execution

A new parallel runner was added in `src/selenium_runner.py` and wired through `src/pipeline.py`. The CLI supports remote execution via `--grid-url` and multiple browser targets via `--grid-browsers`.

Example:
```bash
python main.py "Test login page" --grid-url http://localhost:4444/wd/hub --grid-browsers chrome,firefox
```

### Selenium IDE and Katalon Recorder

Evidence for recorded GUI tests has been added under `docs/gui_testing/`:
- `docs/gui_testing/selenium_ide_login.side` — Selenium IDE login test artifact
- `docs/gui_testing/katalon_recorder_login.md` — Katalon Recorder step summary

This demonstrates at least one GUI test created using both record-and-playback tools.

---

## Challenges faced

1. **AI output format consistency** — LLMs may return markdown-wrapped JSON; solved with `extract_json()` and a strict system prompt.  
2. **Selector stability** — Demo app uses `data-test` attributes; prompts instruct the model to use known selectors (`#user-name`, `#password`, etc.).  
3. **ChromeDriver versioning** — Handled via `webdriver-manager` to avoid manual driver downloads.  
4. **Separation of concerns** — Unit tests mock the browser so CI/local runs do not require Chrome for pytest.

---

## Screenshots checklist (for final presentation)

- [ ] Sauce Demo login page  
- [ ] Terminal: `python main.py "Test login page"`  
- [ ] Generated `latest_test_plan.json` excerpt  
- [ ] HTML report in browser  
- [ ] `pytest -v` output  

---

## Source code locations

| Artifact | Path |
|----------|------|
| Entry point | `main.py` |
| AI generation | `src/ai_generator.py` |
| Validation | `src/test_parser.py` |
| Selenium execution | `src/selenium_runner.py` |
| Reports | `src/report_generator.py` |
| Unit tests | `tests/` |

---

## References

See [REFERENCES.md](REFERENCES.md).
