import pytest

def test_create_task(authenticated_page, tasks_page, page):
    """
    Test creating a new task through the UI.
    """
    tasks_page.navigate("/dashboard/tasks")
    
    initial_count = tasks_page.get_task_count()
    
    tasks_page.open_create_modal()
    tasks_page.fill_form(
        name="E2E Automation Task",
        description="Verify this task is created correctly",
        status="Pending",
        priority="High"
    )
    tasks_page.save_task()
    
    # Wait for table to update
    page.wait_for_timeout(2000)
    
    new_count = tasks_page.get_task_count()
    assert new_count == initial_count + 1
    assert "E2E Automation Task" in tasks_page.table.text_content()

def test_assign_task_to_employee(authenticated_page, tasks_page, page):
    """
    Test the task assignment modal.
    """
    tasks_page.navigate("/dashboard/tasks")
    
    # Click the first 'Users' icon in the table
    # This assumes at least one task exists
    page.locator(".action-btn[title='Assign Employees']").first.click()
    
    # Verify modal appears
    tasks_page.assign_modal.wait_for(state="visible", timeout=5000)
    assert tasks_page.assign_modal.is_visible()
    
    # Select first employee in list
    page.locator(".modal-content input[type='checkbox']").first.click()
    
    # Save assignments
    page.click("text=Save Assignments")
    
    # Modal should close
    page.wait_for_selector(".modal-content", state="hidden")
