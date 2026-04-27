import pytest

def test_create_task(authenticated_page, tasks_page, page):
    """
    Test creating a new task through the UI.
    """
    tasks_page.navigate("/dashboard/tasks")
    
    initial_count = tasks_page.get_task_count()
    
    import time
    unique_name = f"E2E Task {int(time.time())}"
    
    tasks_page.open_create_modal()
    tasks_page.fill_form(
        name=unique_name,
        description="Verify this task is created correctly",
        status="Pending",
        priority="High"
    )
    tasks_page.save_task()
    
    # Wait for table to update
    page.wait_for_timeout(2000)
    
    new_count = tasks_page.get_task_count()
    assert new_count > initial_count
    assert unique_name in tasks_page.table.text_content()

def test_assign_task_to_employee(authenticated_page, tasks_page, employees_page, page):
    """
    Test the task assignment modal.
    """
    # 1. Ensure at least one employee exists
    employees_page.navigate("/dashboard/employees")
    if employees_page.get_employee_count() == 0:
        employees_page.open_add_modal()
        employees_page.fill_form("Task", "Assignee", "task.assignee@example.com", "9998887776")
        employees_page.save_employee()
        page.wait_for_timeout(1000)

    # 2. Ensure at least one task exists
    tasks_page.navigate("/dashboard/tasks")
    if tasks_page.get_task_count() == 0:
        tasks_page.open_create_modal()
        tasks_page.fill_form("Assignment Test", "Desc", "Pending", "Low")
        tasks_page.save_task()
        page.wait_for_timeout(1000)

    # 3. Open assignment modal
    assign_btn = page.locator(".action-btn[title='Assign Employees']").first
    assign_btn.wait_for(state="visible", timeout=10000)
    assign_btn.click()
    
    # Verify modal appears
    tasks_page.assign_modal.wait_for(state="visible", timeout=5000)
    assert tasks_page.assign_modal.is_visible()
    
    # Select first employee in list
    page.locator(".modal-content input[type='checkbox']").first.click()
    
    # Save assignments
    page.click("text=Save Assignments")
    
    # Modal should close
    page.wait_for_selector(".modal-content", state="hidden")
