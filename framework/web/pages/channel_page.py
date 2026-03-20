from framework.web.pages.base_page import BasePage


class ChannelPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.page_panel = '#main-container .view-title', 'Calls/Chat'
        self.page_panel_nav = '#tab-bar .system-nav a.orgItem[tooltip-template="Calls/Chat"]'
        self.create_channel_button = '.create-object-btn.create-channel'
        self.channel_name = '#channel-name'
        self.channel_description = '#channel-description'
        self.channel_submit = 'button[type=submit]'

    def open_panel(self):
        if self.is_visible_by_text(self.page_panel):
            return
        self.page.click(self.page_panel_nav)

    def create_channel(self, name):
        if not self.is_visible_by_text(self.page_panel):
            self.open_panel()
        self.page.click(self.create_channel_button)
        self.page.fill(self.channel_name, name)