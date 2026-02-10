from framework.web.pages.base_page import BasePage


class ChannelPage(BasePage):
    def __init__(self, page):
        super().__init__(page)
        self.channel_name = '#channel-name'
        self.channel_description = '#channel-description'
        self.channel_submit = 'button[type=submit]'

    def open(self, base_url):
        self.page.goto(base_url + '/channels')

    def create_channel(self, name, description):
        self.page.fill(self.channel_name, name)
