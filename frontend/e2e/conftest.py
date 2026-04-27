import time
import pytest
from playwright.sync_api import sync_playwright
from e2e.pages.login_page import LoginPage
from e2e.pages.register_page import RegisterPage
from e2e.pages.dashboard_page import DashboardPage
from e2e.pages.employees_page import EmployeesPage
from e2e.pages.tasks_page import TasksPage
from e2e.pages.profile_page import ProfilePage

# ─── Fixed admin credentials for E2E session ──────────────────────────────────
# We use a known phone. The fixture handles the case where it's already registered.
E2E_ADMIN_PHONE = "7000000001"
E2E_ADMIN_NAME  = "E2E Admin Corp"
E2E_ADMIN_ADDR  = "1 Test Lane"
E2E_ADMIN_CITY  = "Testville"


# ─── Browser / Page fixtures ───────────────────────────────────────────────────

@pytest.fixture(scope="function")
def browser_context():
    """Fresh browser context for every single test to ensure total isolation."""
    with sync_playwright() as p:
        # Use headless=True for stability, but we can switch to False for debugging
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(base_url="http://localhost:3000")
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="function")
def page(browser_context):
    """Fresh page per test."""
    pg = browser_context.new_page()
    yield pg
    # pg.close() is handled by context.close()


# ─── Page-Object fixtures ─────────────────────────────────────────────────────

@pytest.fixture
def login_page(page):
    return LoginPage(page)

@pytest.fixture
def register_page(page):
    return RegisterPage(page)

@pytest.fixture
def dashboard_page(page):
    return DashboardPage(page)

@pytest.fixture
def employees_page(page):
    return EmployeesPage(page)

@pytest.fixture
def tasks_page(page):
    return TasksPage(page)

@pytest.fixture
def profile_page(page):
    return ProfilePage(page)


# ─── Authenticated page fixture ────────────────────────────────────────────────

@pytest.fixture
def authenticated_page(page, login_page, register_page, dashboard_page):
    """
    Returns a page already logged in as admin.

    """
    # Step 1 – Ensure user is registered (idempotent)
    page.on("dialog", lambda d: d.accept())
    register_page.navigate("/register")
    try:
        register_page.register(E2E_ADMIN_NAME, E2E_ADMIN_PHONE,
                               E2E_ADMIN_ADDR, E2E_ADMIN_CITY)
        # Give it a moment to process (success or "already exists")
        page.wait_for_timeout(2000)
    except Exception:
        pass

    # Step 2 – Login with OTP interception
    otp = None
    def capture_otp(response):
        nonlocal otp
        try:
            if "/send-otp" in response.url and response.status == 200:
                otp = response.json().get("otp")
        except Exception: pass

    page.on("response", capture_otp)
    login_page.navigate("/login")
    login_page.login_step_1(E2E_ADMIN_PHONE)

    # Wait for OTP step or dashboard (if already logged in)
    try:
        page.wait_for_selector(".otp-digit", timeout=10000)
        if otp:
            login_page.enter_otp(otp)
        else:
            # Maybe OTP was already sent or there's a delay, wait a bit more
            page.wait_for_timeout(2000)
            if otp: login_page.enter_otp(otp)
    except Exception:
        # If we are already on dashboard, great
        if "/dashboard" in page.url: pass

    # Final check: Must be on dashboard
    page.wait_for_url("**/dashboard", timeout=15000)
    dashboard_page.is_visible()
    
    return page
