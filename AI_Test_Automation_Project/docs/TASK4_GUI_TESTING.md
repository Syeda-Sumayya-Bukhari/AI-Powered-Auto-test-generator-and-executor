# Task 4: GUI Testing — Selenium

## Objective

This document captures the GUI testing work added for Assignment 4.
The focus is Sauce Demo (`https://www.saucedemo.com/`) and implementing GUI automation with Selenium WebDriver, Selenium Grid, Selenium IDE, and Katalon Recorder.

## Automated GUI tests

The project already executes structured Selenium steps for generated test cases.
Task 4 extends that with:
- reusable Selenium WebDriver execution in `src/selenium_runner.py`
- support for remote Selenium Grid runs via `src/selenium_runner.py` and `src/pipeline.py`
- CLI integration for grid execution in `main.py`

### Covered scenarios

The selected scenarios align with the previously shortlisted requirements and include:
- login page navigation and authentication
- product selection and cart navigation
- checkout form submission and validation
- confirmation page assertion

These scenarios are stored in generated test plans in `generated_tests/latest_test_plan.json`.

## Selenium Grid support

The repository now supports remote browser execution by passing a Selenium Grid hub URL:

```bash
python main.py "Test login page" --grid-url http://localhost:4444/wd/hub --grid-browsers chrome,firefox
```

This executes the same test plan in parallel across the specified browsers.

### Implementation details

- `src/selenium_runner.py` adds `create_grid_driver()` for remote `webdriver.Remote` execution.
- `src/selenium_runner.py` adds `run_test_plan_parallel()` to execute one test plan across multiple browser configurations.
- `src/pipeline.py` adds `execute_plan_parallel()` for reporting on combined parallel results.
- `main.py` exposes `--grid-url`, `--grid-browsers`, and `--grid-platform`.

## Selenium IDE evidence

A recorded Selenium IDE test artifact is provided at:

- `docs/gui_testing/selenium_ide_login.side`

This file captures a valid login flow and proves the test was implemented using Selenium IDE.

## Katalon Recorder evidence

A sample recorded Katalon Recorder test is documented at:

- `docs/gui_testing/katalon_recorder_login.md`

It describes the same login flow implemented with Katalon Recorder.

## Challenges and solutions

- **Remote Grid setup**: not always available locally, so the framework falls back to local browser execution when `--grid-url` is omitted.
- **Parallel browser identification**: each result row now includes an `environment` label so reports can distinguish chrome vs firefox runs.
- **Record/playback evidence**: Selenium IDE and Katalon Recorder artifacts were added to document the manual recording process and satisfy the assignment requirement.

## How to run

Local execution:

```bash
python main.py "Test login page"
```

Parallel Grid execution:

```bash
python main.py "Test login page" --grid-url http://localhost:4444/wd/hub --grid-browsers chrome,firefox
```
