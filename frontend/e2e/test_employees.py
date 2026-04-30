import time


def test_add_employee(admin_page, employees_page):
    """
    Test adding a new employee through the UI.
    Uses pre-authenticated admin session.
    """
    employees_page.navigate("/dashboard/employees")

    initial_count = employees_page.get_employee_count()

    unique_suffix = str(int(time.time()))[-6:]
    unique_email = f"e2e.worker.{unique_suffix}@example.com"
    unique_phone = f"1212{unique_suffix}"

    employees_page.open_add_modal()
    employees_page.fill_form(
        first_name="E2E",
        last_name="Worker",
        email=unique_email,
        phone=unique_phone
    )
    employees_page.save_employee()

    admin_page.wait_for_timeout(2000)

    new_count = employees_page.get_employee_count()
    assert new_count > initial_count
    assert "E2E Worker" in employees_page.table.text_content()


def test_view_employee_profile(admin_page, employees_page, profile_page):
    """
    Test viewing an employee's detailed profile.
    Uses pre-authenticated admin session.
    """
    employees_page.navigate("/dashboard/employees")

    # Click the 'View Profile' (Eye icon) for the first employee
    admin_page.locator(".action-btn[title='View Profile']").first.click()

    # Wait for profile page to load
    admin_page.wait_for_url("**/dashboard/employees/*")

    # Verify profile content
    assert profile_page.get_employee_name() != ""
    assert profile_page.assigned_tasks_section.is_visible()

    # Check if login code is displayed
    login_code = profile_page.get_login_code()
    assert login_code.startswith("Emp")
