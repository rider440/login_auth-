import os
import time

# Respect the E2E_HEADLESS env var set by run_all_tests.ps1 -Headless flag
HEADLESS = os.environ.get("E2E_HEADLESS", "0") == "1"
import pytest
from pathlib import Path
from playwright.sync_api import sync_playwright
from e2e.pages.login_page import LoginPage
from e2e.pages.register_page import RegisterPage
from e2e.pages.dashboard_page import DashboardPage
from e2e.pages.employees_page import EmployeesPage
from e2e.pages.tasks_page import TasksPage
from e2e.pages.profile_page import ProfilePage

# ─── Configuration ─────────────────────────────────────────────────────────────

BASE_URL = "http://localhost:3000"
AUTH_DIR = Path("e2e/.auth")
ADMIN_STORAGE = AUTH_DIR / "admin.json"
EMPLOYEE_STORAGE = AUTH_DIR / "employee.json"

E2E_ADMIN_PHONE = "7000000001"
E2E_ADMIN_NAME  = "E2E Admin Corp"
E2E_ADMIN_ADDR  = "1 Test Lane"
E2E_ADMIN_CITY  = "Testville"

E2E_EMP_PHONE = "7000000002"
E2E_EMP_EMAIL = "e2e.employee@example.com"
E2E_EMP_FIRST = "E2E"
E2E_EMP_LAST  = "Employee"

# Ensure auth directory exists
AUTH_DIR.mkdir(exist_ok=True)

# ─── Session Authentication Fixtures ───────────────────────────────────────────

@pytest.fixture(scope="session")
def admin_auth_state():
    """
    One-time login for Admin. Saves state to admin.json.
    """
    print("\n[Auth] Setting up Admin session...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(base_url=BASE_URL)
        page = context.new_page()
        
        login_page = LoginPage(page)
        register_page = RegisterPage(page)
        dashboard_page = DashboardPage(page)

        # 1. Register (Idempotent)
        page.on("dialog", lambda d: d.accept())
        register_page.navigate("/register")
        try:
            register_page.register(E2E_ADMIN_NAME, E2E_ADMIN_PHONE,
                                   E2E_ADMIN_ADDR, E2E_ADMIN_CITY)
            page.wait_for_timeout(2000)
        except Exception: pass

        # 2. Login with OTP interception
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

        # Wait for OTP step
        try:
            page.wait_for_selector(".otp-digit", timeout=10000)
            if not otp: page.wait_for_timeout(2000) # Give extra time if slow
            if otp:
                login_page.enter_otp(otp)
            else:
                raise Exception("Failed to capture OTP for Admin")
        except Exception as e:
            if "/dashboard" not in page.url:
                raise e

        # Final check: Must be on dashboard
        page.wait_for_url("**/dashboard", timeout=15000)
        dashboard_page.is_visible()
        
        # Save state
        context.storage_state(path=ADMIN_STORAGE)
        print(f"[Auth] Admin state saved to {ADMIN_STORAGE}")
        
        browser.close()
    return ADMIN_STORAGE


@pytest.fixture(scope="session")
def employee_auth_state(admin_auth_state):
    """
    One-time setup and login for Employee.
    1. Uses Admin session to ensure Employee exists and get Login Code.
    2. Logs in as Employee and saves state.
    """
    print("\n[Auth] Setting up Employee session...")
    login_code = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # --- PART 1: Get Login Code using Admin session ---
        context = browser.new_context(base_url=BASE_URL, storage_state=ADMIN_STORAGE)
        page = context.new_page()
        
        emp_page = EmployeesPage(page)
        prof_page = ProfilePage(page)
        
        emp_page.navigate("/dashboard/employees")
        
        # Check if our E2E employee exists
        page.wait_for_timeout(2000) # Wait for table load
        table_text = page.locator(".data-table").text_content() if page.locator(".data-table").count() > 0 else ""
        
        if E2E_EMP_EMAIL not in table_text:
            print("[Auth] Creating E2E Employee...")
            emp_page.open_add_modal()
            emp_page.fill_form(E2E_EMP_FIRST, E2E_EMP_LAST, E2E_EMP_EMAIL, E2E_EMP_PHONE)
            emp_page.save_employee()
            page.wait_for_timeout(2000)
        
        # Find the employee in the table and go to profile
        # We look for the row containing the email
        row = page.locator(f"tr:has-text('{E2E_EMP_EMAIL}')")
        row.locator(".action-btn[title='View Profile']").click()
        
        page.wait_for_url("**/dashboard/employees/*")
        login_code = prof_page.get_login_code()
        print(f"[Auth] Captured Login Code for Employee: {login_code}")
        
        context.close()

        # --- PART 2: Login as Employee ---
        context = browser.new_context(base_url=BASE_URL)
        page = context.new_page()
        login_page = LoginPage(page)
        
        login_page.navigate("/login")
        # Assuming login page has a way to switch or handle login code
        # Based on LoginPage.py, enter_login_code exists
        login_page.login_step_1(E2E_EMP_PHONE)
        page.wait_for_selector("#loginCode", timeout=5000)
        login_page.enter_login_code(login_code)
        
        page.wait_for_url("**/dashboard", timeout=10000)
        
        context.storage_state(path=EMPLOYEE_STORAGE)
        print(f"[Auth] Employee state saved to {EMPLOYEE_STORAGE}")
        
        browser.close()
    
    return EMPLOYEE_STORAGE


# ─── Page Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def admin_page(admin_auth_state):
    """
    Returns a page object pre-authenticated as Admin.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(base_url=BASE_URL, storage_state=admin_auth_state)
        page = context.new_page()
        yield page
        context.close()
        browser.close()

@pytest.fixture
def employee_page(employee_auth_state):
    """
    Returns a page object pre-authenticated as Employee.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(base_url=BASE_URL, storage_state=employee_auth_state)
        page = context.new_page()
        yield page
        context.close()
        browser.close()


# ─── Page Object Fixtures ──────────────────────────────────────────────────────

@pytest.fixture
def login_page(admin_page): return LoginPage(admin_page)

@pytest.fixture
def dashboard_page(admin_page): return DashboardPage(admin_page)

@pytest.fixture
def employees_page(admin_page): return EmployeesPage(admin_page)

@pytest.fixture
def tasks_page(admin_page): return TasksPage(admin_page)

@pytest.fixture
def profile_page(admin_page): return ProfilePage(admin_page)

# For employee-specific tests, we might want separate PO instances
@pytest.fixture
def emp_dashboard_page(employee_page): return DashboardPage(employee_page)

@pytest.fixture
def emp_tasks_page(employee_page): return TasksPage(employee_page)
