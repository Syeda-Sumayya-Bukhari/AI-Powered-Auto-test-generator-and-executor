import os

import pytest
from selenium.common.exceptions import WebDriverException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from src.config import BASE_URL, DEFAULT_PASSWORD, DEFAULT_USERNAME
from src.selenium_runner import create_driver


def _should_run_gui_tests() -> bool:
    return os.getenv("RUN_GUI_TESTS", "0").lower() in {"1", "true", "yes"}


@pytest.fixture
def browser() -> "webdriver.Chrome":
    if not _should_run_gui_tests():
        pytest.skip("Skipping live GUI tests. Set RUN_GUI_TESTS=1 to enable them.")

    try:
        driver = create_driver(headless=True)
        yield driver
    except WebDriverException as exc:
        pytest.skip(f"Selenium WebDriver unavailable: {exc}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


def _wait_for_element(driver, selector: str, timeout: int = 10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def _wait_for_clickable(driver, selector: str, timeout: int = 10):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
    )


def _login(driver, username: str, password: str) -> None:
    driver.get(BASE_URL)
    _wait_for_element(driver, "#user-name").send_keys(username)
    _wait_for_element(driver, "#password").send_keys(password)
    _wait_for_clickable(driver, "#login-button").click()
    WebDriverWait(driver, 10).until(EC.url_contains("inventory.html"))


def test_login_page_shows_login_form(browser):
    browser.get(BASE_URL)

    assert _wait_for_element(browser, "#user-name").is_displayed()
    assert _wait_for_element(browser, "#password").is_displayed()
    assert _wait_for_element(browser, "#login-button").is_displayed()


def test_valid_login_redirects_to_inventory(browser):
    _login(browser, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    assert "inventory.html" in browser.current_url
    assert _wait_for_element(browser, ".inventory_list").is_displayed()


def test_add_to_cart_updates_cart_badge_and_cart_page(browser):
    _login(browser, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    add_buttons = browser.find_elements(By.CSS_SELECTOR, ".btn_primary.btn_small.btn_inventory")
    assert add_buttons, "No add-to-cart buttons were found on the inventory page"
    add_buttons[0].click()

    badge = _wait_for_element(browser, ".shopping_cart_badge")
    assert badge.text == "1"

    _wait_for_clickable(browser, ".shopping_cart_link").click()
    WebDriverWait(browser, 10).until(EC.url_contains("cart.html"))

    cart_items = browser.find_elements(By.CSS_SELECTOR, ".cart_item")
    assert len(cart_items) == 1


def test_checkout_flow_completes_order(browser):
    _login(browser, DEFAULT_USERNAME, DEFAULT_PASSWORD)

    add_buttons = browser.find_elements(By.CSS_SELECTOR, ".btn_primary.btn_small.btn_inventory")
    assert add_buttons, "No add-to-cart buttons were found on the inventory page"
    add_buttons[0].click()

    _wait_for_clickable(browser, ".shopping_cart_link").click()
    _wait_for_clickable(browser, "#checkout").click()

    _wait_for_element(browser, "#first-name")
    _wait_for_element(browser, "#first-name").send_keys("Alice")
    _wait_for_element(browser, "#last-name").send_keys("Tester")
    _wait_for_element(browser, "#postal-code").send_keys("12345")
    _wait_for_clickable(browser, "#continue").click()

    _wait_for_element(browser, ".summary_info")
    _wait_for_clickable(browser, "#finish").click()

    try:
        complete_header = _wait_for_element(browser, ".complete-header", timeout=15)
    except TimeoutException as exc:
        pytest.fail(f"Checkout confirmation did not appear: {exc}")

    assert "THANK YOU FOR YOUR ORDER" in complete_header.text.upper()
