from appium import webdriver

from framework.core.config import ProjConfig


class AppiumDriver:
    def __init__(self, caps: dict = None, server_url: str = None):
        self.server_url = server_url or ProjConfig.APPIUM_SERVER
        self.caps = caps or {}
        self.driver = webdriver.Remote(self.server_url, self.caps)


    def quit(self):
        self.driver.quit()