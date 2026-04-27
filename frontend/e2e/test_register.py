import pytest

def test_registration_flow(register_page, login_page, page):
    """
    Test the registration flow and subsequent redirect to login.
    """
    register_page.navigate("/register")
    
    import time
    unique_phone = str(int(time.time()))[-10:] # Last 10 digits of timestamp
    # Handle the registration success alert
    page.on("dialog", lambda dialog: dialog.accept())
    
    # Fill registration form
    register_page.register(
        name="Test Company E2E",
        phone=unique_phone,
        address="123 Test St",
        city="Test City"
    )
    
    # Check if redirected to login
    page.wait_for_url("**/login")
    assert login_page.phone_input.is_visible()
