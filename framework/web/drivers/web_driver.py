# framework/web/drivers/web_driver.py
from playwright.sync_api import sync_playwright


class PlaywrightManager:
    """Singleton - chỉ start sync_playwright() MỘT LẦN duy nhất"""
    _pw = None
    
    @classmethod
    def get(cls):
        if cls._pw is None:
            cls._pw = sync_playwright().start()
        return cls._pw
    
    @classmethod
    def stop(cls):
        if cls._pw:
            cls._pw.stop()
            cls._pw = None
class WebDriver:
    def __init__(self, browser='chromium', headless=True):
        pw = PlaywrightManager.get()  # Dùng chung 1 instance
        
        if browser == 'chromium':
            self.browser = pw.chromium.launch(headless=headless)
        elif browser == 'firefox':
            self.browser = pw.firefox.launch(headless=headless)
        elif browser == 'webkit':
            self.browser = pw.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        self.page = self.browser.new_page()
    def quit(self):
        self.browser.close()
        # KHÔNG gọi self._pw.stop() nữa - PlaywrightManager.stop() sẽ xử lý khi cần