class IPhoneLoginPage:
    def __init__(self, driver):
        self.driver = driver


    def login(self, user, pw):
        d = self.driver
        d.find_element('accessibility id', 'username').send_keys(user)
        d.find_element('accessibility id', 'password').send_keys(pw)
        d.find_element('accessibility id', 'login_btn').click()