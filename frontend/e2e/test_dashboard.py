import pytest

def test_dashboard_content_as_admin(authenticated_page, dashboard_page):
    """
    Verify that the admin dashboard shows correct profile info.
    """
    # authenticated_page fixture handles the login
    assert dashboard_page.is_visible()
    assert "Admin Dashboard" in dashboard_page.get_role_title()
    
    # Check if profile card contains admin info
    assert "Admin User" in dashboard_page.profile_card.text_content()
    assert "9999999999" in dashboard_page.profile_card.text_content()

def test_navigation_to_employees(authenticated_page, page):
    """
    Test navigating to the employees management page from dashboard.
    """
    # Assuming there's a sidebar or link to employees
    # Let's check layout.tsx for links
    page.click("text=Employees") # Common link text
    page.wait_for_url("**/dashboard/employees")
    assert page.locator("h1:has-text('Employees')").is_visible()
