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
