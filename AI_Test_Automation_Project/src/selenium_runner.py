"""Execute structured test cases in a real browser using Selenium WebDriver."""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Any

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from src.config import BASE_URL

DEFAULT_WAIT_SECONDS = 8


@dataclass
class StepResult:
    step_index: int
    action: str
    description: str
    status: str  # PASS | FAIL
    message: str = ""


@dataclass
class TestCaseResult:
    __test__ = False
    test_id: str
    title: str
    expected_output: str
    status: str  # PASS | FAIL
    duration_seconds: float
    module: str = ""
    test_type: str = ""
    environment: str = ""
    steps: list[StepResult] = field(default_factory=list)
    error: str = ""


def find_cached_chromedriver() -> str | None:
    try:
        from pathlib import Path
        wdm_dir = Path.home() / ".wdm" / "drivers" / "chromedriver"
        if wdm_dir.exists():
            drivers = list(wdm_dir.glob("**/chromedriver.exe"))
            if not drivers:
                drivers = list(wdm_dir.glob("**/chromedriver"))
            if drivers:
                drivers.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                return str(drivers[0])
    except Exception:
        pass
    return None


def create_driver(headless: bool = True) -> webdriver.Chrome:
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.page_load_strategy = "eager"
    
    cached_path = find_cached_chromedriver()
    if cached_path:
        service = Service(executable_path=cached_path)
    else:
        service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def create_grid_driver(
    grid_url: str,
    browser_name: str = "chrome",
    platform_name: str = "ANY",
    headless: bool = True,
) -> webdriver.Remote:
    browser_name = browser_name.lower()
    if browser_name == "firefox":
        options = FirefoxOptions()
        options.headless = headless
    else:
        options = Options()
        if headless:
            options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,720")
    options.page_load_strategy = "eager"

    capabilities = options.to_capabilities()
    capabilities["browserName"] = browser_name
    capabilities["platformName"] = platform_name

    return webdriver.Remote(command_executor=grid_url, desired_capabilities=capabilities, options=options)


def _resolve_url(base_url: str, target: str) -> str:
    if target.startswith("http"):
        return target
    path = target if target.startswith("/") else f"/{target}"
    return base_url.rstrip("/") + path


def reset_browser_session(driver: webdriver.Chrome, base_url: str) -> None:
    """Clear cookies and return to login page between test cases."""
    driver.delete_all_cookies()
    driver.get(_resolve_url(base_url, "/"))


def execute_step(
    driver: webdriver.Chrome,
    base_url: str,
    step: dict[str, Any],
    wait_seconds: int = DEFAULT_WAIT_SECONDS,
) -> StepResult:
    action = step.get("action", "")
    target = step.get("target", "")
    value = step.get("value", "")
    description = step.get("description", action)

    try:
        if action == "navigate":
            driver.get(_resolve_url(base_url, target or "/"))
        elif action == "type":
            element = WebDriverWait(driver, wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, target))
            )
            element.clear()
            element.send_keys(value)
        elif action == "click":
            element = WebDriverWait(driver, wait_seconds).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, target))
            )
            element.click()
        elif action == "select":
            element = WebDriverWait(driver, wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, target))
            )
            Select(element).select_by_value(value)
        elif action == "assert_text":
            element = WebDriverWait(driver, wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, target))
            )
            if value not in element.text:
                return StepResult(
                    0,
                    action,
                    description,
                    "FAIL",
                    f"Expected text '{value}' not in '{element.text}'",
                )
        elif action == "assert_url":
            WebDriverWait(driver, wait_seconds).until(lambda d: target in d.current_url)
        elif action == "assert_element":
            WebDriverWait(driver, wait_seconds).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, target))
            )
        else:
            return StepResult(0, action, description, "FAIL", f"Unknown action: {action}")

        return StepResult(0, action, description, "PASS")
    except (TimeoutException, NoSuchElementException) as exc:
        return StepResult(0, action, description, "FAIL", str(exc))
    except Exception as exc:  # noqa: BLE001 - capture for report
        return StepResult(0, action, description, "FAIL", str(exc))


def run_test_case(
    test_case: dict[str, Any],
    base_url: str | None = None,
    headless: bool = True,
    driver: webdriver.Chrome | None = None,
    environment: str = "local",
) -> TestCaseResult:
    """Run a single test case. Reuses *driver* when provided (caller manages lifecycle)."""
    url = base_url or BASE_URL
    test_id = test_case.get("id", "UNKNOWN")
    title = test_case.get("title", "Untitled")
    expected = test_case.get("expected_output", "")
    steps = test_case.get("steps", [])

    own_driver = driver is None
    if own_driver:
        driver = create_driver(headless=headless)

    assert driver is not None
    step_results: list[StepResult] = []
    start = time.perf_counter()
    overall_status = "PASS"
    error_msg = ""

    try:
        for index, step in enumerate(steps, start=1):
            result = execute_step(driver, url, step)
            result.step_index = index
            step_results.append(result)
            if result.status == "FAIL":
                overall_status = "FAIL"
                error_msg = result.message
                break
    finally:
        if own_driver:
            driver.quit()

    duration = time.perf_counter() - start
    return TestCaseResult(
        test_id=test_id,
        title=title,
        expected_output=expected,
        status=overall_status,
        duration_seconds=round(duration, 2),
        module=test_case.get("module", ""),
        test_type=test_case.get("test_type", ""),
        environment=environment,
        steps=step_results,
        error=error_msg,
    )


def run_test_plan(
    plan: dict[str, Any],
    headless: bool = True,
    on_progress: Callable[[int, int, str], None] | None = None,
    driver_factory: Callable[[bool], webdriver.Chrome | webdriver.Remote] | None = None,
    environment: str = "local",
) -> list[TestCaseResult]:
    """
    Execute all test cases using one shared browser (much faster than opening a new browser per case).
    """
    base_url = plan.get("application_url", BASE_URL)
    cases = plan.get("test_cases", [])
    total = len(cases)
    results: list[TestCaseResult] = []

    if not cases:
        return results

    if driver_factory is None:
        driver_factory = lambda active_headless: create_driver(headless=active_headless)

    driver = driver_factory(headless)
    try:
        for index, test_case in enumerate(cases, start=1):
            test_id = test_case.get("id", f"case-{index}")
            if on_progress:
                on_progress(index, total, test_id)
            if index > 1:
                reset_browser_session(driver, base_url)
            results.append(
                run_test_case(
                    test_case,
                    base_url=base_url,
                    headless=headless,
                    driver=driver,
                    environment=environment,
                )
            )
    finally:
        driver.quit()

    return results


def run_test_plan_parallel(
    plan: dict[str, Any],
    browser_configs: list[dict[str, Any]],
    *,
    headless: bool = True,
    on_progress: Callable[[int, int, str], None] | None = None,
) -> list[TestCaseResult]:
    """Execute the same test plan in parallel across multiple browser configurations."""

    if not browser_configs:
        return []

    def _run_for_config(config: dict[str, Any]) -> list[TestCaseResult]:
        browser_name = config.get("browser_name", "chrome")
        platform_name = config.get("platform_name", "ANY")
        grid_url = config.get("grid_url")
        environment = config.get("environment") or f"{browser_name}@{platform_name}"
        active_headless = config.get("headless", headless)

        def driver_factory(active_headless: bool) -> webdriver.Chrome | webdriver.Remote:
            if grid_url:
                return create_grid_driver(
                    grid_url,
                    browser_name=browser_name,
                    platform_name=platform_name,
                    headless=active_headless,
                )
            return create_driver(headless=active_headless)

        return run_test_plan(
            plan,
            headless=active_headless,
            on_progress=on_progress,
            driver_factory=driver_factory,
            environment=environment,
        )

    results: list[TestCaseResult] = []
    with ThreadPoolExecutor(max_workers=len(browser_configs)) as executor:
        futures = {executor.submit(_run_for_config, config): config for config in browser_configs}
        for future in as_completed(futures):
            results.extend(future.result())

    return results
