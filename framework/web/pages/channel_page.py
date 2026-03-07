from framework.web.pages.base_page import BasePage


class ChannelPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.channel_name = '#channel-name'
        self.channel_description = '#channel-description'
        self.channel_submit = 'button[type=submit]'

    def open_panel(self):
        if self.is_visible_by_text('#main-container .view-title', 'Calls/Chat'):
            return
        self.page.click('#tab-bar .system-nav a.orgItem[tooltip-template="Calls/Chat"]')

    def create_channel(self, name, description):
        self.page.fill(self.channel_name, name)
