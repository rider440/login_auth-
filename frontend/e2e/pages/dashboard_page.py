from e2e.pages.base_page import BasePage

class DashboardPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.header = page.locator("h1")
        self.welcome_message = page.locator(".subtitle")
        self.profile_card = page.locator(".glass-card").first
        self.task_table = page.locator(".data-table")

    def get_role_title(self):
        return self.header.text_content()

    def get_welcome_text(self):
        return self.welcome_message.text_content()

    def is_visible(self):
        self.header.wait_for(state="visible", timeout=10000)
        return self.header.is_visible()
