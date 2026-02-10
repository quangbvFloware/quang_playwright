from .base_page import BasePage


class WebLoginPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.username = '#login-form-username'
        self.password = '#txtPassword'
        self.submit = 'button[type=submit]'


    def open(self, base_url):
        self.page.goto(base_url + '/signin')


    def login(self, user, pw):
        self.page.fill(self.username, user)
        self.page.fill(self.password, pw)
        self.page.click(self.submit)