from e2e.conftest import E2E_ADMIN_NAME, E2E_ADMIN_PHONE

def test_dashboard_content_as_admin(authenticated_page, dashboard_page):
    """
    Verify that the admin dashboard shows correct profile info.
    """
    # authenticated_page fixture handles the login
    assert dashboard_page.is_visible()
    assert "Admin Dashboard" in dashboard_page.get_role_title()
    
    # Check if profile card contains admin info
    dashboard_page.profile_card.wait_for(state="visible", timeout=5000)
    content = dashboard_page.profile_card.text_content()
    assert E2E_ADMIN_NAME in content
    assert E2E_ADMIN_PHONE in content

def test_navigation_to_employees(authenticated_page, page):
    """
    Test navigating to the employees management page from dashboard.
    """
    # Assuming there's a sidebar or link to employees
    # Let's check layout.tsx for links
    page.click("text=Employees") # Common link text
    page.wait_for_url("**/dashboard/employees")
    assert page.locator("h1:has-text('Employees')").is_visible()
