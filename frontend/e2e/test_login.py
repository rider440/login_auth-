import pytest
import re

def test_admin_login_flow(login_page, register_page, dashboard_page, page):
    """
    Test the full admin login flow including OTP interception.
    """
    phone = "9999999999"
    
    # 1. Ensure user is registered
    register_page.navigate("/register")
    register_page.register("Admin User", phone, "123 Admin St", "Admin City")
    page.wait_for_timeout(1000)

    # 2. Navigate to login
    login_page.navigate("/login")
    
    # 2. Enter registered phone number (using the one from our backend tests if it exists)
    # For E2E, we might need to register first or use a known seed.
    phone = "9999999999"
    
    # Listen for the OTP response
    otp = None
    def handle_response(response):
        nonlocal otp
        if "/send-otp" in response.url and response.status == 200:
            data = response.json()
            otp = data.get("otp")

    page.on("response", handle_response)
    
    login_page.login_step_1(phone)
    
    # Wait for step 2 (OTP)
    page.wait_for_selector(".otp-digit")
    
    assert otp is not None, "OTP was not captured from response"
    
    # 3. Enter OTP
    login_page.enter_otp(otp)
    
    # 4. Verify redirect to dashboard
    page.wait_for_url("**/dashboard", timeout=10000)
    assert dashboard_page.is_visible()
    assert "Admin Dashboard" in dashboard_page.get_role_title()

def test_invalid_login_shows_error(login_page, page):
    """
    Test that entering an unregistered phone number shows an error.
    """
    login_page.navigate("/login")
    login_page.login_step_1("0000000000") # Unregistered
    
    # Wait for error message
    login_page.error_message.wait_for(state="visible")
    assert "not registered" in login_page.error_message.text_content()
