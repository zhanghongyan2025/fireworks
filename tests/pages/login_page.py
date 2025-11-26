
from playwright.sync_api import sync_playwright, Page


class LoginPage:
    def __init__(self, page: Page):
        self.page = page
        self.password = page.get_by_role("textbox", name="请输入加密锁密码")
        self.login_button = page.get_by_text("登录")

    def navigate(self, fd_base_url: str):
        self.page.goto(f"{fd_base_url}/login")

    def fill_password(self, login_password: str):
            self.password.fill(login_password)

    def click_login_button(self):
        self.login_button.click()
