"""Unit tests for Selenium runner helpers (no live browser)."""

from unittest.mock import MagicMock, patch

import pytest

from src.selenium_runner import (
    StepResult,
    _resolve_url,
    create_grid_driver,
    execute_step,
    run_test_case,
    run_test_plan_parallel,
)


def test_resolve_url_relative():
    assert _resolve_url("https://www.saucedemo.com/", "/") == "https://www.saucedemo.com/"


def test_resolve_url_absolute():
    url = _resolve_url("https://www.saucedemo.com/", "https://other.com/page")
    assert url == "https://other.com/page"


@patch("src.selenium_runner.WebDriverWait")
def test_execute_step_navigate(mock_wait):
    driver = MagicMock()
    step = {"action": "navigate", "target": "/", "description": "Go home"}
    result = execute_step(driver, "https://www.saucedemo.com/", step)
    assert result.status == "PASS"
    driver.get.assert_called_once()


@patch("src.selenium_runner.create_driver")
def test_run_test_case_stops_on_first_failure(mock_create_driver):
    driver = MagicMock()
    mock_create_driver.return_value = driver

    failing_step = StepResult(1, "click", "bad step", "FAIL", "boom")

    with patch("src.selenium_runner.execute_step", return_value=failing_step):
        test_case = {
            "id": "TC-X",
            "title": "Fail fast",
            "expected_output": "n/a",
            "steps": [{"action": "click"}, {"action": "click"}],
        }
        result = run_test_case(test_case, base_url="https://example.com/", headless=True)

    assert result.status == "FAIL"
    assert len(result.steps) == 1
    driver.quit.assert_called_once()


@patch("src.selenium_runner.webdriver.Remote")
def test_create_grid_driver_remote(mock_remote):
    mock_remote.return_value = MagicMock()
    driver = create_grid_driver(
        "http://grid:4444/wd/hub",
        browser_name="chrome",
        platform_name="LINUX",
        headless=True,
    )
    assert driver is mock_remote.return_value
    assert mock_remote.call_count == 1
    assert mock_remote.call_args.kwargs["command_executor"] == "http://grid:4444/wd/hub"


@patch("src.selenium_runner.run_test_plan")
def test_run_test_plan_parallel_executes_each_browser(mock_run_test_plan):
    plan = {"test_cases": []}
    browser_configs = [
        {"browser_name": "chrome", "platform_name": "ANY", "environment": "chrome", "headless": True},
        {"browser_name": "firefox", "platform_name": "LINUX", "environment": "firefox", "headless": True},
    ]

    mock_run_test_plan.side_effect = [[], []]
    results = run_test_plan_parallel(plan, browser_configs)

    assert results == []
    assert mock_run_test_plan.call_count == 2
    first_call = mock_run_test_plan.call_args_list[0][1]
    second_call = mock_run_test_plan.call_args_list[1][1]
    assert first_call["environment"] == "chrome"
    assert second_call["environment"] == "firefox"
