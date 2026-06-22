# Test Coverage — Positive & Negative Scenarios

**Assignment requirement:** *Ensure comprehensive test coverage, including positive and negative test scenarios.*

---

## 1. Integration / GUI tests (Selenium on Sauce Demo)

**17 automated test cases** across **4 modules**. Each module includes **positive** (happy path) and **negative** (invalid data, wrong expectations, edge cases) scenarios.

| Module | Positive tests | Negative tests | Total |
|--------|----------------|----------------|-------|
| **Login** | TC-L01 (valid login) | TC-L02 (wrong password), TC-L03 (locked user), TC-L04 (empty username), TC-L05 (wrong URL assert) | 5 |
| **Inventory** | TC-I01 (product list), TC-I02 (product name), TC-I04 (sort) | TC-I03 (fake product name) | 4 |
| **Cart** | TC-C01 (add item), TC-C02 (badge=1), TC-C04 (cart page) | TC-C03 (badge=99 wrong) | 4 |
| **Checkout** | TC-K01 (full checkout) | TC-K02 (empty form), TC-K03 (wrong message), TC-K04 (empty cart) | 4 |

### What “positive” vs “negative” means

| Type | Meaning | Example |
|------|---------|---------|
| **Positive** | Valid input / correct expected behavior | Login with `standard_user` → inventory page |
| **Negative** | Invalid input, boundary, or wrong assertion | Wrong password → error message; or intentional wrong expected URL → test **fails** |

**Note:** A negative **scenario** can still **PASS** when the application correctly rejects bad input (e.g. TC-L02). Some negative tests **FAIL** on purpose (wrong assertion) to prove the runner detects defects (e.g. TC-L05).

### Execution summary (typical full run)

- **~11 PASS** / **~6 FAIL** (~65% pass rate) — demonstrates both outcomes in the HTML report.

---

## 2. Unit tests (pytest on framework code)

**25+ unit tests** on critical Python components with positive and negative cases:

| Component | Positive (valid input) | Negative (invalid / error) |
|-----------|------------------------|----------------------------|
| `test_parser.py` | Valid plan accepted | Missing scenarios, empty cases, bad scenario ID, invalid action, missing ID, empty steps |
| `test_ai_generator.py` | JSON parse, mock plan structure | — |
| `test_report_generator.py` | Pass/fail counts | Mixed PASS+FAIL payload |
| `test_selenium_runner.py` | URL resolve, navigate step | Fail-fast on step failure |
| `test_coverage_catalog.py` | Each module has +/− tests | — |
| `test_pipeline.py` | Requirement builder, module filter | — |

Run: `pytest -v`

---

## 3. How to demonstrate for submission

1. Run `python ui_app.py` → **All Modules** → **Generate & Execute**
2. Screenshot HTML report showing **Type** column (positive/negative) and mixed Pass/Fail
3. Run `pytest -v` and screenshot unit test results
4. Include this document (or the tables from `ASSIGNMENT_REPORT.md`) in your report
