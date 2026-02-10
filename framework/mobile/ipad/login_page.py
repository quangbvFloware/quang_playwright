class IPadLoginPage:
    def __init__(self, driver):
        self.driver = driver


    def login(self, user, pw):
        d = self.driver
        # ipad may have different ids or xpaths
        d.find_element('xpath', "//XCUIElementTypeTextField[@name='ipad_username']").send_keys(user)
        d.find_element('xpath', "//XCUIElementTypeSecureTextField[@name='ipad_password']").send_keys(pw)
        d.find_element('xpath', "//XCUIElementTypeButton[@name='ipad_login']").click()