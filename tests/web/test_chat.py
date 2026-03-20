from playwright.sync_api import expect

from framework.utils import parallel_get
from framework.utils.logging_util import logger
from framework.web.pages.login_page import WebLoginPage


def test_chat(api_clients, web_clients):
    # Start both API and Web clients in parallel (truly parallel!)
    # web_user1, web_user2 = parallel_get(
        # (api_clients, 'user1'),
        # (web_clients, 'user1'),
        # (web_clients, 'user2')
    # )
    web_user1 = web_clients.user1
    web_user2 = web_clients.user2
    # owner_api.api.collections.get(dict(page_size=10, modified_gte=0))
    web_user1.channel_page.open_panel()
