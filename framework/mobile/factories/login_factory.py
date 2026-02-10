from framework.mobile.ipad.login_page import IPadLoginPage
from framework.mobile.iphone.login_page import IPhoneLoginPage


class LoginPageFactory:
    @staticmethod
    def get(driver):
        caps = driver.capabilities
        device = (caps.get('deviceName') or '').lower()
        if 'ipad' in device:
            return IPadLoginPage(driver)
        return IPhoneLoginPage(driver)