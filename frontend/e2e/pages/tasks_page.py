from e2e.pages.base_page import BasePage

class TasksPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.create_task_btn = page.locator("text=Create Task")
        self.task_name_input = page.locator("label:has-text('Task Name') + input")
        self.description_input = page.locator("textarea")
        self.status_select = page.locator("label:has-text('Status') + select")
        self.priority_select = page.locator("label:has-text('Priority') + select")
        self.save_button = page.locator("button:has-text('Save Task')")
        self.table = page.locator(".data-table")
        self.assign_modal = page.locator(".modal-content:has-text('Assign Employees')")

    def open_create_modal(self):
        self.create_task_btn.click()

    def fill_form(self, name, description, status="Pending", priority="Normal"):
        self.task_name_input.fill(name)
        self.description_input.fill(description)
        self.status_select.select_option(status)
        self.priority_select.select_option(priority)

    def save_task(self):
        self.save_button.click()

    def get_task_count(self):
        # Wait for any loading spinner to disappear
        self.page.wait_for_selector(".animate-spin", state="hidden", timeout=10000)
        
        # If the table isn't there, it might be the empty state (count 0)
        if self.table.count() == 0:
            return 0
            
        self.table.wait_for(state="visible", timeout=5000)
        return self.table.locator("tbody tr").count()
