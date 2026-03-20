import functools
import os
import time
from urllib.parse import urlparse

import pytest
import requests

from framework.api.helpers import auth_helper
from framework.api.request_patching import patched_request
from framework.consts.consts_common import APIServiceType
from framework.consts.project import (CONFIG_DIR, RESOURCES_PEM_DIR,
                                      RESOURCES_YAML_DIR)
from framework.core.config import ProjConfig
from framework.setup_client import (setup_api_client, setup_ios_client,
                                    setup_mac_client, setup_web_client,
                                    wait_all)
from framework.utils import DotDict, string_util
from framework.utils.logging_util import logger

# --------- #
# DIRECTORY #
# --------- #


@pytest.fixture(scope="session", autouse=True)
def proj_config(runtime_profile):
    env = runtime_profile["env"]
    ProjConfig.load_config(env)
    return ProjConfig.get_config()


@pytest.fixture(scope="session")
def api_config():
    return ProjConfig.get_config(load_api=True)


@pytest.fixture(scope="session")
def public_key(api_config):
    decoded_pk = auth_helper.get_public_key(api_config["env"])
    ProjConfig.set_config("public_key", decoded_pk)
    return decoded_pk


# ========================================
# API CLIENTS - owner, member, member_2
# ========================================


@pytest.fixture(scope="session")
def api_clients(proj_config):
    """
    API clients with unified structure (DotDict with auto-execution)

    Structure:
        - owner: Main user API client
        - member: Member 1 API client
        - member_2: Member 2 API client

    Usage (DotDict auto-executes setup function):
        >>> def test_api(api_clients):
        >>>     # Simple access - DotDict automatically calls setup_api_client()
        >>>     owner = api_clients.owner
        >>>     # owner is now an APIClient instance - use directly!
        >>>     response = owner.api.collections.get()
        >>>
        >>>     # Multiple clients - automatic parallel execution
        >>>     owner = api_clients.owner      # Thread 1 starts
        >>>     member = api_clients.member    # Thread 2 starts
        >>>     member_2 = api_clients.member_2  # Thread 3 starts
        >>>     # All 3 are created in parallel automatically!

    Note: First access creates client, subsequent accesses return cached instance.
    """
    return DotDict(
        user1=dict(
            function=setup_api_client,
            user=proj_config["user"],
            password=proj_config["password"],
        ),
        user2=dict(
            function=setup_api_client,
            user=proj_config["user2"],
            password=proj_config["password"],
        ),
        user3=dict(
            function=setup_api_client,
            user=proj_config["user3"],
            password=proj_config["password"],
        ),
    )


# ========================================
# WEB CLIENTS - user1, user2, user3
# ========================================


@pytest.fixture(scope="session")
def web_clients(proj_config, runtime_profile, request):
    """
    Web clients with unified structure (DotDict with auto-execution)

    Structure:
        - user1: Main user web browser
        - user2: Member 1 web browser
        - user3: Member 2 web browser

    Usage (DotDict auto-executes setup function):
        >>> def test_web(web_clients):
        >>>     # Simple access - DotDict automatically calls setup_web_client()
        >>>     user1 = web_clients.user1
        >>>     # owner is now a WebClient instance - use directly!
        >>>     user1.channel_page.create_channel("Test")
        >>>
        >>>     # Multiple browsers - automatic parallel execution
        >>>     user1 = web_clients.user1
        >>>     user2 = web_clients.user2
        >>>     user3 = web_clients.user3
        >>>     # All 3 browsers start in parallel automatically!

    Note: First access creates browser, subsequent accesses return cached instance.
    """
    headless = runtime_profile.get("headless", False)

    yield DotDict(
        user1=dict(
            function=setup_web_client,
            user=proj_config["user"],
            browser=runtime_profile.get("web_browser", "chromium"),
            password=proj_config["password"],
            headless=headless,
        ),
        user2=dict(
            function=setup_web_client,
            user=proj_config["user2"],
            browser=runtime_profile.get("web_browser", "chromium"),
            password=proj_config["password"],
            headless=headless,
        ),
        user3=dict(
            function=setup_web_client,
            user=proj_config["user3"],
            browser=runtime_profile.get("web_browser", "chromium"),
            password=proj_config["password"],
            headless=headless,
        ),
    )
    from framework.web.drivers.web_driver import PlaywrightManager
    PlaywrightManager.stop()


# ========================================
# MAC CLIENTS - user1, user2, user3
# ========================================


@pytest.fixture(scope="session")
def mac_clients(proj_config):
    """
    Mac clients with unified structure (DotDict with auto-execution)

    Structure:
        - user1: Mac instance 1
        - user2: Mac instance 2
        - user3: Mac instance 3

    Usage (DotDict auto-executes setup function):
        >>> def test_mac(mac_clients):
        >>>     # Simple access - DotDict automatically calls setup_mac_client()
        >>>     user1 = mac_clients.user1
        >>>     # user1 is now a MacDriver instance - use directly!
        >>>     user1.click_element('button')
        >>>
        >>>     # Multiple Macs - automatic parallel execution
        >>>     user1 = mac_clients.user1
        >>>     user2 = mac_clients.user2
        >>>     user3 = mac_clients.user3
        >>>     # Both start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        user1=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
        user2=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
        user3=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
    )


# ========================================
# IPHONE CLIENTS - user1, user2, user3
# ========================================


@pytest.fixture(scope="session")
def iphone_clients(proj_config):
    """
    iPhone clients with unified structure (DotDict with auto-execution)

    Structure:
        - user1: iPhone instance 1
        - user2: iPhone instance 2
        - member_2: iPhone instance 3

    Usage (DotDict auto-executes setup function):
        >>> def test_iphone(iphone_clients):
        >>>     # Simple access - DotDict automatically calls setup_ios_client()
        >>>     user1 = iphone_clients.user1
        >>>     # user1 is now an AppiumDriver instance - use directly!
        >>>     owner.find_element('app_icon').click()
        >>>
        >>>     # Multiple iPhones - automatic parallel execution
        >>>     user1 = iphone_clients.user1
        >>>     user2 = iphone_clients.user2
        >>>     user3 = iphone_clients.user3
        >>>     # All 3 start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        user1=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="iphone_caps.json",
        ),
        user2=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="iphone_caps.json",
        ),
        user3=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="iphone_caps.json",
        ),
    )


# ========================================
# IPAD CLIENTS - user1, user2, user3
# ========================================


@pytest.fixture(scope="session")
def ipad_clients(proj_config):
    """
    iPad clients with unified structure (DotDict with auto-execution)

    Structure:
        - user1: iPad (9th generation)
        - user2: iPad (10th generation)
        - user3: iPad Pro

    Usage (DotDict auto-executes setup function):
        >>> def test_ipad(ipad_clients):
        >>>     # Simple access - DotDict automatically calls setup_ios_client()
        >>>     user1 = ipad_clients.user1
        >>>     # user1 is now an AppiumDriver instance - use directly!
        >>>     user1.find_element('app_icon').click()
        >>>
        >>>     # Multiple iPads - automatic parallel execution
        >>>     user1 = ipad_clients.user1  # iPad 9th gen
        >>>     user2 = ipad_clients.user2  # iPad 10th gen
        >>>     user3 = ipad_clients.user3  # iPad Pro
        >>>     # All 3 start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        user1=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad (9th generation)",
            caps_file="ipad_caps.json",
        ),
        user2=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad (10th generation)",
            caps_file="ipad_caps.json",
        ),
        user3=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad Pro (12.9-inch)",
            caps_file="ipad_caps.json",
        ),
    )


# ========================================
# BACKWARD COMPATIBILITY FIXTURES
# ========================================


@pytest.fixture
def mac(mac_clients):
    """
    Legacy mac fixture - for backward compatibility
    Uses mac_clients.user1 (DotDict auto-executes setup_mac_client)

    Note: The unified fixture pattern is preferred.
    Use mac_clients directly for better control.
    """
    driver = mac_clients.user1  # DotDict auto-executes and returns driver
    yield driver
    try:
        driver.quit()
    except Exception:
        pass


@pytest.fixture
def iphone(iphone_clients):
    """
    Legacy iphone fixture - for backward compatibility
    Uses iphone_clients.user1 (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use iphone_clients directly for better control.
    """
    driver = iphone_clients.user1  # DotDict auto-executes and returns driver
    yield driver
    driver.quit()


@pytest.fixture
def ipad(ipad_clients):
    """
    Legacy ipad fixture - for backward compatibility
    Uses ipad_clients.user1 (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use ipad_clients directly for better control.
    """
    driver = ipad_clients.user1  # DotDict auto-executes and returns driver
    yield driver
    driver.quit()


@pytest.fixture(params=["iphone", "ipad"])
def ios(request, iphone_clients, ipad_clients):
    """
    Legacy ios fixture with parameterization - for backward compatibility
    Maps to iphone_clients.user1 or ipad_clients.user1 based on param
    (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use iphone_clients/ipad_clients directly for better control.
    """
    if request.param == "iphone":
        driver = iphone_clients.user1  # DotDict auto-executes
    else:
        driver = ipad_clients.user1  # DotDict auto-executes

    yield driver
    driver.quit()


@pytest.fixture(scope="session", autouse=True, name=f"patch_requests-{string_util.unique_uuid1()}")
def patch_requests(proj_config):
    """
    Monkey-patch requests.Session.request
    Auto log mọi API request/response - không cần sửa code khác.
    """
    def patch(f):
        @patched_request
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            __tracebackhide__ = True
            result = f(*args, **kwargs)
            return result

        return wrapper

    requests.Session.request = patch(requests.Session.request)
