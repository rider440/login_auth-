from e2e.pages.base_page import BasePage

class RegisterPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.name_input = page.locator("#name")
        self.phone_input = page.locator("#number")
        self.address_input = page.locator("#address")
        self.city_input = page.locator("#city")
        self.submit_button = page.locator("button[type='submit']")
        self.login_link = page.locator("text=Login")

    def register(self, name: str, phone: str, address: str, city: str):
        self.name_input.fill(name)
        self.phone_input.fill(phone)
        self.address_input.fill(address)
        self.city_input.fill(city)
        self.submit_button.click()
