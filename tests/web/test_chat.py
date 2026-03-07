from playwright.sync_api import expect

from framework.utils import parallel_get
from framework.utils.logging_util import logger
from framework.web.pages.login_page import WebLoginPage


def test_chat(api_clients, web_clients):
    # Start both API and Web clients in parallel (truly parallel!)
    # owner_api, owner_web = parallel_get(
    #     (api_clients, 'owner'),
    #     (web_clients, 'owner')
    # )
    owner_api = api_clients.owner
    # owner_web = web_clients.owner
    owner_api.api.collections.get(dict(page_size=10, modified_gte=0))
    # owner_web.channel_page.open_panel()
