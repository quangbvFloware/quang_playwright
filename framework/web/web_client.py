from playwright.sync_api import expect

from framework.core.config import ProjConfig
from framework.utils import encrypt_util
from framework.web.drivers.web_driver import WebDriver
from framework.web.pages.login_page import WebLoginPage


class WebClient:
    """
    WebClient quản lý browser và các pages
    Tự động đăng nhập và cung cấp access đến các page objects
    """
    
    def __init__(self, driver=None, browser='chromium', headless=False, 
                 email=None, password=None, auto_login=True):
        """
        Args:
            driver: WebDriver instance (nếu đã khởi tạo sẵn)
            browser: Loại browser ('chromium', 'firefox', 'webkit') - chỉ dùng nếu driver=None
            headless: Chạy headless mode (default False) - chỉ dùng nếu driver=None
            email: Email đăng nhập (default từ Config)
            password: Password (default từ Config)
            auto_login: Tự động login khi khởi tạo (default True)
        """
        # Khởi tạo driver nếu chưa có
        if driver is None:
            self.driver = WebDriver(browser=browser, headless=headless)
            self._own_driver = True  # Đánh dấu để biết cần close driver khi xong
        else:
            self.driver = driver
            self._own_driver = False
        
        self.page = self.driver.page
        
        # Lấy credentials từ Config nếu không truyền
        self.email = email or ProjConfig.get_config('user')
        self.username = email.partition('@')[0]
        self.password = password or ProjConfig.get_config('password')
        self.base_url = ProjConfig.get_config('base_url')['web']
        
        # Khởi tạo login page
        self.login_page = WebLoginPage(self.page)
        
        # Auto login nếu cần
        if auto_login:
            self.login()
    
    def login(self, username=None, password=None):
        """Đăng nhập vào hệ thống"""
        username = username or self.username
        password = password or self.password
        
        self.login_page.open(self.base_url)
        self.login_page.login(username, password)
        
        # Verify login thành công
        expect(self.page.locator('#tab-bar')).to_be_visible(timeout=15000)
        return self
    
    def open(self, path=''):
        """Mở URL"""
        if path.startswith('http'):
            url = path
        else:
            url = self.base_url + path
        self.page.goto(url)
        return self
    
    def close(self):
        """Đóng browser (chỉ đóng nếu WebClient tự tạo driver)"""
        if self._own_driver:
            self.driver.quit()
    
    # ===== Helper methods từ BasePage =====
    def wait_for(self, selector, timeout=5000):
        """Chờ element xuất hiện"""
        return self.page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_visible(self, selector, timeout=10000):
        """Chờ element visible"""
        return self.page.wait_for_selector(selector, state='visible', timeout=timeout)
    
    def wait_for_url(self, url_pattern, timeout=10000):
        """Chờ URL thay đổi"""
        return self.page.wait_for_url(url_pattern, timeout=timeout)
    
    # ===== Common actions =====
    def click(self, selector):
        """Click element"""
        return self.page.click(selector)
    
    def fill(self, selector, text):
        """Điền text vào input"""
        return self.page.fill(selector, text)
    
    def get_text(self, selector):
        """Lấy text của element"""
        return self.page.locator(selector).text_content()
    
    def is_visible(self, selector):
        """Check element có visible không"""
        return self.page.locator(selector).is_visible()
    
    # ===== Page Object Access =====
    @property
    def channel_page(self):
        """Access ChannelPage nếu có"""
        # Lazy loading - chỉ import khi cần
        from framework.web.pages.channel_page import ChannelPage
        return ChannelPage(self.page)
    
    # Thêm các page khác tương tự...