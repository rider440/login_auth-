from e2e.pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.phone_input = page.locator("#phone")
        self.continue_button = page.locator("button[type='submit']")
        self.otp_digits = page.locator(".otp-digit")
        self.login_code_input = page.locator("#loginCode")
        self.register_link = page.locator("text=Register")
        self.error_message = page.locator("div[style*='background: rgba(239, 68, 68, 0.1)']")

    def login_step_1(self, phone: str):
        self.phone_input.fill(phone)
        self.continue_button.click()

    def enter_otp(self, otp: str):
        for i, digit in enumerate(otp):
            self.otp_digits.nth(i).fill(digit)
        self.continue_button.click()

    def enter_login_code(self, code: str):
        self.login_code_input.fill(code)
        self.continue_button.click()

    def go_to_register(self):
        self.register_link.click()
