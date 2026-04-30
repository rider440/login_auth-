"""
Registration & Login Flow Tests
These tests spin up their own fresh browser context since they test
the unauthenticated flows (register, login with OTP).
"""
import time
import pytest
from playwright.sync_api import sync_playwright
from e2e.conftest import BASE_URL
from e2e.pages.register_page import RegisterPage
from e2e.pages.login_page import LoginPage


@pytest.fixture
def fresh_page():
    """
    A standalone fresh browser page with NO saved auth state.
    Used only by tests that test the unauthenticated flow.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(base_url=BASE_URL)
        page = context.new_page()
        yield page
        context.close()
        browser.close()


def test_registration_flow(fresh_page):
    """
    Test the registration flow and subsequent redirect to login.
    A new unique phone number is used each run so it is idempotent.
    """
    register_page = RegisterPage(fresh_page)
    login_page = LoginPage(fresh_page)

    register_page.navigate("/register")

    unique_phone = str(int(time.time()))[-10:]
    fresh_page.on("dialog", lambda dialog: dialog.accept())

    register_page.register(
        name="Test Company E2E",
        phone=unique_phone,
        address="123 Test St",
        city="Test City"
    )

    # After successful registration, should redirect to /login
    fresh_page.wait_for_url("**/login", timeout=10000)
    assert login_page.phone_input.is_visible()


def test_invalid_login_shows_error(fresh_page):
    """
    An unregistered phone number should show 'not registered' error.
    """
    login_page = LoginPage(fresh_page)

    login_page.navigate("/login")
    login_page.login_step_1("0000000000")  # definitely not registered

    login_page.error_message.wait_for(state="visible", timeout=5000)
    assert "not registered" in login_page.error_message.text_content()
