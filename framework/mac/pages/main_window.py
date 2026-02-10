class MainWindow:
    def __init__(self, driver):
        self.driver = driver


    def click_login(self):
        btn = self.driver.find(role="AXButton", title="Login")
        if btn:
            btn.Press()