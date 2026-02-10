# framework/web/drivers/web_driver.py
from playwright.sync_api import sync_playwright


class WebDriver:
    def __init__(self, browser='chromium', headless=True):
        """
        Args:
            browser: 'chromium', 'firefox', hoặc 'webkit'
            headless: Chạy headless mode hay không
        """
        self._pw = sync_playwright().start()
        
        # Chọn browser type
        if browser == 'chromium':
            self.browser = self._pw.chromium.launch(headless=headless)
        elif browser == 'firefox':
            self.browser = self._pw.firefox.launch(headless=headless)
        elif browser == 'webkit':
            self.browser = self._pw.webkit.launch(headless=headless)
        else:
            raise ValueError(f"Unsupported browser: {browser}")
        
        self.page = self.browser.new_page()

    def goto(self, url):
        return self.page.goto(url)

    def quit(self):
        self.browser.close()
        self._pw.stop()