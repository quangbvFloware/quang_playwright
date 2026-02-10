class BaseMobilePage:
    def __init__(self, driver):
        self.driver = driver


    def is_ipad(self):
        name = (self.driver.capabilities.get('deviceName') or '').lower()
        return 'ipad' in name


    def is_iphone(self):
        return not self.is_ipad()