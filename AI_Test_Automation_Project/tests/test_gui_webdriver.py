# tests/test_gui_webdriver.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from src.selenium_runner import create_driver

BASE_URL = "https://www.saucedemo.com"

@pytest.fixture
def driver():
    d = create_driver(headless=True)
    d.implicitly_wait(5)
    yield d
    d.quit()

def login(driver, username="standard_user", password="secret_sauce"):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "user-name").clear()
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").clear()
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()

# ──── LOGIN TESTS ────
def test_TC_L01_valid_login(driver):
    login(driver)
    assert "inventory" in driver.current_url

def test_TC_L02_invalid_password(driver):
    login(driver, password="wrongpass")
    error = driver.find_element(By.CLASS_NAME, "error-message-container")
    assert "Username and password do not match" in error.text

def test_TC_L03_locked_user(driver):
    login(driver, username="locked_out_user")
    error = driver.find_element(By.CLASS_NAME, "error-message-container")
    assert "locked out" in error.text

def test_TC_L04_empty_username(driver):
    login(driver, username="", password="secret_sauce")
    error = driver.find_element(By.CLASS_NAME, "error-message-container")
    assert "Username is required" in error.text

# ──── INVENTORY TESTS ────
def test_TC_I01_product_list_visible(driver):
    login(driver)
    items = driver.find_elements(By.CLASS_NAME, "inventory_item")
    assert len(items) > 0

def test_TC_I04_sort_price_low_to_high(driver):
    login(driver)
    dropdown = Select(driver.find_element(By.CLASS_NAME, "product_sort_container"))
    dropdown.select_by_value("lohi")
    prices = [float(p.text.replace("$","")) for p in 
              driver.find_elements(By.CLASS_NAME, "inventory_item_price")]
    assert prices == sorted(prices)

# ──── CART TESTS ────
def test_TC_C01_add_backpack_to_cart(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    badge = driver.find_element(By.CLASS_NAME, "shopping_cart_badge")
    assert badge.text == "1"

def test_TC_C04_cart_page_shows_item(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    assert "cart" in driver.current_url

# ──── CHECKOUT TESTS ────
def test_TC_K01_complete_checkout(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "first-name").send_keys("Sumayya")
    driver.find_element(By.ID, "last-name").send_keys("Test")
    driver.find_element(By.ID, "postal-code").send_keys("44000")
    driver.find_element(By.ID, "continue").click()
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "finish").is_displayed()
    )
    driver.find_element(By.ID, "finish").click()
    header = driver.find_element(By.CLASS_NAME, "complete-header")
    assert "Thank you" in header.text

def test_TC_K02_checkout_empty_form(driver):
    login(driver)
    driver.find_element(By.ID, "add-to-cart-sauce-labs-backpack").click()
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()
    driver.find_element(By.ID, "checkout").click()
    driver.find_element(By.ID, "continue").click()
    error = driver.find_element(By.CLASS_NAME, "error-message-container")
    assert "First Name is required" in error.text