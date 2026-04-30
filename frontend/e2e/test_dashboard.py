from e2e.conftest import E2E_ADMIN_NAME, E2E_ADMIN_PHONE


def test_dashboard_content_as_admin(admin_page, dashboard_page):
    """
    Verify that the admin dashboard shows correct profile info.
    Uses pre-authenticated admin session (no login needed).
    """
    admin_page.goto("/dashboard")
    assert dashboard_page.is_visible()
    assert "Admin Dashboard" in dashboard_page.get_role_title()

    dashboard_page.profile_card.wait_for(state="visible", timeout=5000)
    content = dashboard_page.profile_card.text_content()
    assert E2E_ADMIN_NAME in content
    assert E2E_ADMIN_PHONE in content


def test_navigation_to_employees(admin_page):
    """
    Test navigating to the employees management page from dashboard sidebar.
    """
    admin_page.goto("/dashboard")
    admin_page.click("text=Employees")
    admin_page.wait_for_url("**/dashboard/employees")
    assert admin_page.locator("h1:has-text('Employees')").is_visible()


def test_navigation_to_tasks(admin_page):
    """
    Test navigating to the tasks management page from dashboard sidebar.
    """
    admin_page.goto("/dashboard")
    admin_page.click("text=Tasks")
    admin_page.wait_for_url("**/dashboard/tasks")
    assert admin_page.locator("h1:has-text('Tasks')").is_visible()
