from playwright.sync_api import expect

from framework.utils.logging_util import logger
from framework.web.pages.login_page import WebLoginPage


def test_login_web(web, proj_config):
    page = WebLoginPage(web)
    page.open(proj_config.web)
    page.login(proj_config.username, proj_config.password)
    expect(web.locator('#tab-bar')).to_be_visible(timeout=15000)
