from e2e.conftest import E2E_ADMIN_PHONE, E2E_ADMIN_NAME, E2E_ADMIN_ADDR, E2E_ADMIN_CITY


def test_admin_login_flow(login_page, register_page, dashboard_page, page):
    """
    Full admin login flow: register (idempotent) → OTP intercept → dashboard verify.
    """
    # 1. Accept any success alert from registration
    page.on("dialog", lambda d: d.accept())

    # 2. Try to register — silently skip if phone already exists
    register_page.navigate("/register")
    try:
        register_page.register(E2E_ADMIN_NAME, E2E_ADMIN_PHONE,
                               E2E_ADMIN_ADDR, E2E_ADMIN_CITY)
        page.wait_for_timeout(1500)
    except Exception:
        pass  # already registered — that's fine

    # 3. Intercept the OTP from the /send-otp response
    otp = None

    def capture_otp(response):
        nonlocal otp
        try:
            if "/send-otp" in response.url and response.status == 200:
                otp = response.json().get("otp")
        except Exception:
            pass

    page.on("response", capture_otp)

    # 4. Navigate to login and enter phone
    login_page.navigate("/login")
    login_page.login_step_1(E2E_ADMIN_PHONE)

    # 5. Wait for OTP input screen
    page.wait_for_selector(".otp-digit", timeout=8000)
    assert otp is not None, "OTP was not captured from the /send-otp response"

    # 6. Enter OTP
    login_page.enter_otp(otp)

    # 7. Verify redirect to dashboard
    page.wait_for_url("**/dashboard", timeout=10000)
    assert dashboard_page.is_visible()
    assert "Admin Dashboard" in dashboard_page.get_role_title()


def test_invalid_login_shows_error(login_page, page):
    """
    An unregistered phone number should show 'not registered' error.
    """
    login_page.navigate("/login")
    login_page.login_step_1("0000000000")  # definitely not registered

    login_page.error_message.wait_for(state="visible", timeout=5000)
    assert "not registered" in login_page.error_message.text_content()
