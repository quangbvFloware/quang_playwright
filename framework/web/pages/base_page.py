class BasePage:
    def __init__(self, page):
        self.page = page

    def wait_for(self, selector, timeout=5000):
        return self.page.wait_for_selector(selector, timeout=timeout)
    
    def wait_for_visible(self, selector, timeout=10000):
        """Chờ element visible"""
        return self.page.wait_for_selector(selector, state='visible', timeout=timeout)
    
    def wait_for_url(self, url_pattern, timeout=10000):
        """Chờ URL thay đổi sau login"""
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
    
    def is_visible_by_text(self, selector, text):
        """Check element có visible không"""
        return self.page.locator(selector).get_by_text(text).is_visible()
