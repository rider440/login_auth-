import time


def test_create_task(admin_page, tasks_page):
    """
    Test creating a new task through the UI (Admin only).
    """
    tasks_page.navigate("/dashboard/tasks")
    admin_page.wait_for_timeout(2000)

    initial_count = tasks_page.get_task_count()
    unique_name = f"E2E Task {int(time.time())}"

    tasks_page.open_create_modal()
    tasks_page.fill_form(
        name=unique_name,
        description="Verify this task is created correctly",
        status="Pending",
        priority="High"
    )
    tasks_page.save_task()

    admin_page.wait_for_timeout(2000)

    new_count = tasks_page.get_task_count()
    assert new_count > initial_count
    assert unique_name in tasks_page.table.text_content()


def test_view_task_report_history(admin_page, tasks_page):
    """
    Admin clicks 'Reports History' button and modal appears.
    """
    tasks_page.navigate("/dashboard/tasks")
    admin_page.wait_for_timeout(2000)

    # Ensure at least one task exists
    if tasks_page.get_task_count() == 0:
        tasks_page.open_create_modal()
        tasks_page.fill_form("History Test Task", "desc", "Pending", "Normal")
        tasks_page.save_task()
        admin_page.wait_for_timeout(2000)

    # Click history button on first task
    tasks_page.history_btn.first.wait_for(state="visible", timeout=10000)
    tasks_page.history_btn.first.click()

    # Verify report modal appears
    tasks_page.report_modal.wait_for(state="visible", timeout=5000)
    assert tasks_page.report_modal.is_visible()

    # Close the modal
    admin_page.click("text=Close")
    tasks_page.report_modal.wait_for(state="hidden", timeout=5000)


def test_edit_task(admin_page, tasks_page):
    """
    Admin edits an existing task.
    """
    tasks_page.navigate("/dashboard/tasks")
    admin_page.wait_for_timeout(2000)

    # Ensure at least one task exists
    if tasks_page.get_task_count() == 0:
        tasks_page.open_create_modal()
        tasks_page.fill_form("Edit Test Task", "original desc", "Pending", "Low")
        tasks_page.save_task()
        admin_page.wait_for_timeout(2000)

    # Click Edit button (pencil icon, no title attr) — second action-btn after history
    edit_btn = admin_page.locator("tbody tr").first.locator(".action-btn").nth(1)
    edit_btn.wait_for(state="visible", timeout=5000)
    edit_btn.click()

    # Modal should open in edit mode with "Edit Task" heading
    admin_page.wait_for_selector("h2:has-text('Edit Task')", timeout=5000)

    # Change priority to High
    tasks_page.priority_select.select_option("High")
    tasks_page.save_task()

    admin_page.wait_for_timeout(1500)
    # Verify the table still loads
    assert tasks_page.table.is_visible()
