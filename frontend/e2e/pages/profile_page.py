from e2e.pages.base_page import BasePage

class ProfilePage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.back_button = page.locator("text=Back to Employees")
        self.employee_name = page.locator("h2").first
        self.assigned_tasks_section = page.locator("h2:has-text('Assigned Tasks')")
        self.login_code_display = page.locator("h3:has-text('Login Code:')")

    def get_employee_name(self):
        self.employee_name.wait_for(state="visible", timeout=5000)
        return self.employee_name.text_content()

    def get_login_code(self):
        text = self.login_code_display.text_content()
        # Extract the code part
        return text.split("Login Code:")[-1].strip()
