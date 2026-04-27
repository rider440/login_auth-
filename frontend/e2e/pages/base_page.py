from playwright.sync_api import Page, Response

class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = "http://localhost:3000"

    def navigate(self, path: str = ""):
        self.page.goto(f"{self.base_url}{path}")

    def wait_for_load(self):
        self.page.wait_for_load_state("networkidle")

    def get_title(self):
        return self.page.title()
