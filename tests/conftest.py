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
        owner=dict(
            function=setup_api_client,
            user=proj_config["user"],
            password=proj_config["password"],
        ),
        member=dict(
            function=setup_api_client,
            user=proj_config["member_prefix"] + "1" + proj_config["domain"],
            password=proj_config["password"],
        ),
        member_2=dict(
            function=setup_api_client,
            user=proj_config["member_prefix"] + "2" + proj_config["domain"],
            password=proj_config["password"],
        ),
    )


# ========================================
# WEB CLIENTS - owner, member, member_2
# ========================================


@pytest.fixture(scope="session")
def web_clients(proj_config, runtime_profile):
    """
    Web clients with unified structure (DotDict with auto-execution)

    Structure:
        - owner: Main user web browser
        - member: Member 1 web browser
        - member_2: Member 2 web browser

    Usage (DotDict auto-executes setup function):
        >>> def test_web(web_clients):
        >>>     # Simple access - DotDict automatically calls setup_web_client()
        >>>     owner = web_clients.owner
        >>>     # owner is now a WebClient instance - use directly!
        >>>     owner.channel_page.create_channel("Test")
        >>>
        >>>     # Multiple browsers - automatic parallel execution
        >>>     owner = web_clients.owner
        >>>     member = web_clients.member
        >>>     member_2 = web_clients.member_2
        >>>     # All 3 browsers start in parallel automatically!

    Note: First access creates browser, subsequent accesses return cached instance.
    """
    headless = runtime_profile.get("headless", False)

    return DotDict(
        owner=dict(
            function=setup_web_client,
            user=proj_config["user"],
            password=proj_config["password"],
            headless=headless,
        ),
        member=dict(
            function=setup_web_client,
            user=proj_config["member_prefix"] + "1" + proj_config["domain"],
            password=proj_config["password"],
            headless=headless,
        ),
        member_2=dict(
            function=setup_web_client,
            user=proj_config["member_prefix"] + "2" + proj_config["domain"],
            password=proj_config["password"],
            headless=headless,
        ),
    )


# ========================================
# MAC CLIENTS - owner, member, member_2
# ========================================


@pytest.fixture(scope="session")
def mac_clients(proj_config):
    """
    Mac clients with unified structure (DotDict with auto-execution)

    Structure:
        - owner: Mac instance 1
        - member: Mac instance 2
        - member_2: Mac instance 3

    Usage (DotDict auto-executes setup function):
        >>> def test_mac(mac_clients):
        >>>     # Simple access - DotDict automatically calls setup_mac_client()
        >>>     owner = mac_clients.owner
        >>>     # owner is now a MacDriver instance - use directly!
        >>>     owner.click_element('button')
        >>>
        >>>     # Multiple Macs - automatic parallel execution
        >>>     owner = mac_clients.owner
        >>>     member = mac_clients.member
        >>>     # Both start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        owner=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
        member=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
        member_2=dict(
            function=setup_mac_client, bundle_id=None, caps_file="mac_caps.json"
        ),
    )


# ========================================
# IPHONE CLIENTS - owner, member, member_2
# ========================================


@pytest.fixture(scope="session")
def iphone_clients(proj_config):
    """
    iPhone clients with unified structure (DotDict with auto-execution)

    Structure:
        - owner: iPhone instance 1
        - member: iPhone instance 2
        - member_2: iPhone instance 3

    Usage (DotDict auto-executes setup function):
        >>> def test_iphone(iphone_clients):
        >>>     # Simple access - DotDict automatically calls setup_ios_client()
        >>>     owner = iphone_clients.owner
        >>>     # owner is now an AppiumDriver instance - use directly!
        >>>     owner.find_element('app_icon').click()
        >>>
        >>>     # Multiple iPhones - automatic parallel execution
        >>>     owner = iphone_clients.owner
        >>>     member = iphone_clients.member
        >>>     # Both start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        owner=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="ios_caps.json",
        ),
        member=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="ios_caps.json",
        ),
        member_2=dict(
            function=setup_ios_client,
            device_type="iphone",
            device_name=None,
            caps_file="ios_caps.json",
        ),
    )


# ========================================
# IPAD CLIENTS - owner, member, member_2
# ========================================


@pytest.fixture(scope="session")
def ipad_clients(proj_config):
    """
    iPad clients with unified structure (DotDict with auto-execution)

    Structure:
        - owner: iPad (9th generation)
        - member: iPad (10th generation)
        - member_2: iPad Pro

    Usage (DotDict auto-executes setup function):
        >>> def test_ipad(ipad_clients):
        >>>     # Simple access - DotDict automatically calls setup_ios_client()
        >>>     owner = ipad_clients.owner
        >>>     # owner is now an AppiumDriver instance - use directly!
        >>>     owner.find_element('app_icon').click()
        >>>
        >>>     # Multiple iPads - automatic parallel execution
        >>>     owner = ipad_clients.owner  # iPad 9th gen
        >>>     member = ipad_clients.member  # iPad 10th gen
        >>>     member_2 = ipad_clients.member_2  # iPad Pro
        >>>     # All 3 start in parallel automatically!

    Note: First access creates driver, subsequent accesses return cached instance.
    """
    return DotDict(
        owner=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad (9th generation)",
            caps_file="ios_caps.json",
        ),
        member=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad (10th generation)",
            caps_file="ios_caps.json",
        ),
        member_2=dict(
            function=setup_ios_client,
            device_type="ipad",
            device_name="iPad Pro (12.9-inch)",
            caps_file="ios_caps.json",
        ),
    )


# ========================================
# BACKWARD COMPATIBILITY FIXTURES
# ========================================


@pytest.fixture
def mac(mac_clients):
    """
    Legacy mac fixture - for backward compatibility
    Uses mac_clients.owner (DotDict auto-executes setup_mac_client)

    Note: The unified fixture pattern is preferred.
    Use mac_clients directly for better control.
    """
    driver = mac_clients.owner  # DotDict auto-executes and returns driver
    yield driver
    try:
        driver.quit()
    except Exception:
        pass


@pytest.fixture
def iphone(iphone_clients):
    """
    Legacy iphone fixture - for backward compatibility
    Uses iphone_clients.owner (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use iphone_clients directly for better control.
    """
    driver = iphone_clients.owner  # DotDict auto-executes and returns driver
    yield driver
    driver.quit()


@pytest.fixture
def ipad(ipad_clients):
    """
    Legacy ipad fixture - for backward compatibility
    Uses ipad_clients.owner (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use ipad_clients directly for better control.
    """
    driver = ipad_clients.owner  # DotDict auto-executes and returns driver
    yield driver
    driver.quit()


@pytest.fixture(params=["iphone", "ipad"])
def ios(request, iphone_clients, ipad_clients):
    """
    Legacy ios fixture with parameterization - for backward compatibility
    Maps to iphone_clients.owner or ipad_clients.owner based on param
    (DotDict auto-executes setup_ios_client)

    Note: The unified fixture pattern is preferred.
    Use iphone_clients/ipad_clients directly for better control.
    """
    if request.param == "iphone":
        driver = iphone_clients.owner  # DotDict auto-executes
    else:
        driver = ipad_clients.owner  # DotDict auto-executes

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
