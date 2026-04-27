import pytest

def test_add_employee(authenticated_page, employees_page, page):
    """
    Test adding a new employee through the UI.
    """
    employees_page.navigate("/dashboard/employees")
    
    initial_count = employees_page.get_employee_count()
    
    employees_page.open_add_modal()
    employees_page.fill_form(
        first_name="E2E",
        last_name="Worker",
        email="e2e.worker@example.com",
        phone="1112223334"
    )
    employees_page.save_employee()
    
    # Wait for table to update
    page.wait_for_timeout(2000)
    
    new_count = employees_page.get_employee_count()
    assert new_count == initial_count + 1
    assert "E2E Worker" in employees_page.table.text_content()

def test_view_employee_profile(authenticated_page, employees_page, profile_page, page):
    """
    Test viewing an employee's detailed profile.
    """
    employees_page.navigate("/dashboard/employees")
    
    # Click the 'View Profile' (Eye icon) for the first employee
    page.locator(".action-btn[title='View Profile']").first.click()
    
    # Wait for profile page to load
    page.wait_for_url("**/dashboard/employees/*")
    
    # Verify profile content
    assert profile_page.get_employee_name() != ""
    assert profile_page.assigned_tasks_section.is_visible()
    
    # Check if login code is displayed
    login_code = profile_page.get_login_code()
    assert login_code.startswith("Emp")
