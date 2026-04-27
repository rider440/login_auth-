import pytest
from playwright.sync_api import sync_playwright
from e2e.pages.login_page import LoginPage
from e2e.pages.register_page import RegisterPage
from e2e.pages.dashboard_page import DashboardPage
from e2e.pages.employees_page import EmployeesPage
from e2e.pages.tasks_page import TasksPage
from e2e.pages.profile_page import ProfilePage

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(base_url="http://localhost:3000")
        yield context
        browser.close()

@pytest.fixture
def page(browser_context):
    page = browser_context.new_page()
    yield page
    page.close()

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

@pytest.fixture
def authenticated_page(page, login_page, register_page):
    """
    Returns a page that is already logged in as admin.
    Ensures the test user is registered first.
    """
    phone = "9999999999"
    
    # 1. Try to register (it's okay if it fails because user already exists)
    register_page.navigate("/register")
    register_page.register("Admin User", phone, "123 Admin St", "Admin City")
    
    # Wait a bit or check for success/error
    page.wait_for_timeout(1000) 
    
    # 2. Login
    otp = None
    def handle_response(response):
        nonlocal otp
        if "/send-otp" in response.url and response.status == 200:
            otp = response.json().get("otp")

    page.on("response", handle_response)
    
    login_page.navigate("/login")
    login_page.login_step_1(phone)
    
    # Wait for OTP step
    try:
        page.wait_for_selector(".otp-digit", timeout=5000)
        if otp:
            login_page.enter_otp(otp)
            page.wait_for_url("**/dashboard", timeout=5000)
    except Exception:
        # If .otp-digit doesn't appear, maybe login failed.
        pass
    
    return page
