from e2e.pages.base_page import BasePage

class EmployeesPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.add_employee_btn = page.locator("text=Add Employee")
        self.first_name_input = page.locator("input[placeholder='e.g. John']")
        self.last_name_input = page.locator("input[placeholder='e.g. Doe']")
        self.email_input = page.locator("input[type='email']")
        self.phone_input = page.locator("label:has-text('Phone Number') + input")
        self.save_button = page.locator("button:has-text('Save Employee')")
        self.update_button = page.locator("button:has-text('Update Employee')")
        self.cancel_button = page.locator("button:has-text('Cancel')")
        self.table = page.locator(".data-table")

    def open_add_modal(self):
        self.add_employee_btn.click()

    def fill_form(self, first_name, last_name, email, phone):
        self.first_name_input.fill(first_name)
        self.last_name_input.fill(last_name)
        self.email_input.fill(email)
        self.phone_input.fill(phone)

    def save_employee(self):
        self.save_button.click()

    def get_employee_count(self):
        return self.table.locator("tbody tr").count()
