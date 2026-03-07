# framework/setup_client.py
import atexit
from concurrent.futures import Future, ThreadPoolExecutor
from enum import Enum
from threading import Lock
from typing import Callable, Optional, Union

from framework.api.api_client import APIClient
from framework.consts.consts_common import APIServiceType, ClientType
from framework.core.config import ProjConfig
from framework.mac.drivers.mac_driver import MacDriver
from framework.mobile.drivers.appium_driver import AppiumDriver
from framework.utils.logging_util import logger
from framework.web.web_client import WebClient


class ClientExecutor:
    """
    Global thread pool executor for parallel client creation
    Singleton pattern - shared across all setup functions
    """
    _instance = None
    _lock = Lock()
    _executor = None
    _max_workers = 10
    _clients = []  # Track all clients for cleanup
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._executor = ThreadPoolExecutor(max_workers=cls._max_workers)
                    # Register cleanup on exit
                    atexit.register(cls.cleanup)
        return cls._instance
    
    @classmethod
    def submit(cls, fn: Callable, *args, **kwargs) -> Future:
        """
        Submit a function to run in thread pool
        
        Returns:
            Future object
        """
        instance = cls()
        return cls._executor.submit(fn, *args, **kwargs)
    
    @classmethod
    def track_client(cls, client):
        """Track client for cleanup"""
        cls._clients.append(client)
        return client
    
    @classmethod
    def cleanup(cls):
        """Cleanup all clients and shutdown executor"""
        logger.debug(f"🧹 Cleaning up {len(cls._clients)} clients...")
        
        for client in cls._clients:
            try:
                if hasattr(client, 'close'):
                    client.close()
                elif hasattr(client, 'quit'):
                    client.quit()
            except Exception as e:
                logger.error(f"Error closing client: {e}")
        
        if cls._executor:
            cls._executor.shutdown(wait=True)
            logger.debug("✓ All clients cleaned up")


def _create_api_client_sync(
    user: str,
    password: str,
    device_uid: str = "",
    app_id: str = "",
    fake: bool = False,
    internal_group: Optional[int] = None,
    service_type: Union[bool, APIServiceType] = APIServiceType.API,
    is_existed: Optional[bool] = None,
    **kwargs
) -> Union[tuple, APIClient]:
    """Internal sync function to create API client"""
    client = APIClient(
        email=user,
        password=password,
        auto_login=True,
        device_uid=device_uid,
        app_id=app_id,
        fake=fake,
        internal_group=internal_group,
        is_web=service_type == APIServiceType.WEB,
        is_2fa=service_type == APIServiceType.ADMIN,
        is_existed=is_existed,
        **kwargs
    )
    ClientExecutor.track_client(client)
    return client


def setup_api_client(
    user: str = "",
    password: str = "",
    *,
    wait: bool = False,  # NEW: Wait for completion or return Future
    device_uid: str = "",
    app_id: str = "",
    fake: bool = False,
    internal_group: Optional[int] = None,
    service_type: Union[bool, APIServiceType] = APIServiceType.API,
    is_existed: Optional[bool] = None,
    **kwargs
) -> Union[tuple, APIClient, Future]:
    """
    Setup API client - runs in separate thread
    
    Args:
        user: Username/email
        password: Password
        wait: If True, wait for completion. If False, return Future (default: False)
        ... (other args same as before)
    
    Returns:
        If wait=True: APIClient or (headers, username) tuple
        If wait=False: Future object
    
    Example:
        >>> # Async - return immediately, runs in background
        >>> future1 = setup_api_client('user1@test.com', 'pass', service_type=APIServiceType.API)
        >>> future2 = setup_api_client('user2@test.com', 'pass', service_type=APIServiceType.API)
        >>> # ... do other work ...
        >>> client1 = future1.result()  # Wait when needed
        >>> client2 = future2.result()
        
        >>> # Sync - wait for completion
        >>> client = setup_api_client('user@test.com', 'pass', service_type=APIServiceType.API, wait=True)
    """
    # Submit to thread pool - returns immediately
    future = ClientExecutor.submit(
        _create_api_client_sync,
        user, password,
        device_uid=device_uid,
        app_id=app_id,
        fake=fake,
        internal_group=internal_group,
        service_type=service_type,
        is_existed=is_existed,
        **kwargs
    )
    
    # Return Future or wait for result
    if wait:
        return future.result()
    return future


def _create_web_client_sync(
    user: str,
    password: str,
    browser: str = 'chromium',
    headless: bool = False,
    auto_login: bool = True,
    **kwargs
) -> WebClient:
    """Internal sync function to create web client"""
    client = WebClient(
        browser=browser,
        headless=headless,
        email=user,
        password=password,
        auto_login=auto_login
    )
    # ClientExecutor.track_client(client)
    return client


def setup_web_client(
    user: str = "",
    password: str = "",
    *,
    wait: bool = False,  # NEW: Wait for completion or return Future
    browser: str = 'chromium',
    headless: bool = False,
    auto_login: bool = True,
    **kwargs
) -> Union[WebClient, Future]:
    """
    Setup web client - runs in separate thread
    
    Args:
        user: Username/email
        password: Password
        wait: If True, wait for completion. If False, return Future (default: False)
        browser: Browser type
        headless: Run in headless mode
        auto_login: Auto login after creation
    
    Returns:
        If wait=True: WebClient instance
        If wait=False: Future object
    
    Example:
        >>> # Parallel execution - 3 browsers starting simultaneously
        >>> future1 = setup_web_client('user1@test.com', 'pass')
        >>> future2 = setup_web_client('user2@test.com', 'pass')
        >>> future3 = setup_web_client('user3@test.com', 'pass')
        >>> 
        >>> # Continue with other work...
        >>> logger.debug("Browsers starting in background...")
        >>> 
        >>> # Wait when needed
        >>> client1 = future1.result()
        >>> client2 = future2.result()
        >>> client3 = future3.result()
        >>> logger.debug("All browsers ready!")
    """
    # future = ClientExecutor.submit(
    #     _create_web_client_sync,
    #     user, password,
    #     browser=browser,
    #     headless=headless,
    #     auto_login=auto_login,
    #     **kwargs
    # )
    
    # if wait:
    #     return future.result()
    # return future
    return _create_web_client_sync(user, password, browser, headless, auto_login, **kwargs)


def _create_mac_client_sync(
    bundle_id: Optional[str] = None,
    caps_file: str = 'mac_caps.json',
    **kwargs
) -> MacDriver:
    """Internal sync function to create mac client"""
    caps = ProjConfig.load_caps(caps_file)
    if bundle_id:
        caps['bundleId'] = bundle_id
    
    driver = MacDriver(caps['bundleId'])
    ClientExecutor.track_client(driver)
    return driver


def setup_mac_client(
    user: str = "",
    password: str = "",
    *,
    wait: bool = False,
    bundle_id: Optional[str] = None,
    caps_file: str = 'mac_caps.json',
    **kwargs
) -> Union[MacDriver, Future]:
    """Setup Mac client - runs in separate thread"""
    future = ClientExecutor.submit(
        _create_mac_client_sync,
        bundle_id=bundle_id,
        caps_file=caps_file,
        **kwargs
    )
    
    if wait:
        return future.result()
    return future


def _create_ios_client_sync(
    device_type: str = 'iphone',
    device_name: Optional[str] = None,
    caps_file: str = 'ios_caps.json',
    **kwargs
) -> AppiumDriver:
    """Internal sync function to create iOS client"""
    caps = ProjConfig.load_caps(caps_file)
    
    if device_type == 'ipad':
        caps['deviceName'] = device_name or 'iPad (9th generation)'
    elif device_name:
        caps['deviceName'] = device_name
    
    driver = AppiumDriver(caps=caps)
    ClientExecutor.track_client(driver)
    return driver


def setup_ios_client(
    user: str = "",
    password: str = "",
    *,
    wait: bool = False,
    device_type: str = 'iphone',
    device_name: Optional[str] = None,
    caps_file: str = 'ios_caps.json',
    **kwargs
) -> Union[AppiumDriver, Future]:
    """Setup iOS client - runs in separate thread"""
    future = ClientExecutor.submit(
        _create_ios_client_sync,
        device_type=device_type,
        device_name=device_name,
        caps_file=caps_file,
        **kwargs
    )
    
    if wait:
        return future.result()
    return future


def setup_client(
    client_type: Union[str, ClientType],
    user: str = "",
    password: str = "",
    *,
    wait: bool = False,  # NEW: Wait parameter
    **kwargs
) -> Union[APIClient, WebClient, MacDriver, AppiumDriver, tuple, Future]:
    """
    Universal client setup - runs in separate thread
    
    Args:
        client_type: Type of client
        user: Username
        password: Password
        wait: Wait for completion (True) or return Future (False)
        **kwargs: Client-specific arguments
    
    Returns:
        If wait=True: Client instance
        If wait=False: Future object
    
    Example:
        >>> # Start 5 clients in parallel - ALL START IMMEDIATELY
        >>> f1 = setup_client('api', 'user1@test.com', 'pass', service_type=APIServiceType.API)
        >>> f2 = setup_client('web', 'user2@test.com', 'pass', browser='firefox')
        >>> f3 = setup_client('web', 'user3@test.com', 'pass', browser='chromium')
        >>> f4 = setup_client('mac', bundle_id='com.app')
        >>> f5 = setup_client('iphone')
        >>> 
        >>> logger.debug("All 5 clients starting in parallel...")
        >>> 
        >>> # Wait for all
        >>> clients = [f.result() for f in [f1, f2, f3, f4, f5]]
        >>> logger.debug("All clients ready!")
    """
    if isinstance(client_type, str):
        try:
            client_type = ClientType(client_type.lower())
        except ValueError:
            valid_types = [t.value for t in ClientType]
            raise ValueError(f"Invalid client_type '{client_type}'. Valid: {valid_types}")
    
    if client_type == ClientType.API:
        return setup_api_client(user, password, wait=wait, **kwargs)
    
    elif client_type == ClientType.WEB:
        return setup_web_client(user, password, wait=wait, **kwargs)
    
    elif client_type == ClientType.MAC:
        return setup_mac_client(user, password, wait=wait, **kwargs)
    
    elif client_type in [ClientType.IPHONE, ClientType.IPAD]:
        device_type = 'ipad' if client_type == ClientType.IPAD else 'iphone'
        return setup_ios_client(user, password, wait=wait, device_type=device_type, **kwargs)
    
    else:
        raise ValueError(f"Unsupported client_type: {client_type}")


# Helper utilities
def wait_all(*futures: Future):
    """
    Wait for all futures to complete
    
    Example:
        >>> f1 = setup_client('api', 'user1@test.com', 'pass')
        >>> f2 = setup_client('web', 'user2@test.com', 'pass')
        >>> f3 = setup_client('mac')
        >>> 
        >>> clients = wait_all(f1, f2, f3)
        >>> logger.debug(f"Got {len(clients)} clients")
    """
    return [f.result() for f in futures]


def as_completed(*futures: Future):
    """
    Yield futures as they complete
    
    Example:
        >>> futures = [
        ...     setup_client('web', f'user{i}@test.com', 'pass')
        ...     for i in range(10)
        ... ]
        >>> 
        >>> for i, client in enumerate(as_completed(*futures), 1):
        ...     logger.debug(f"Client {i}/10 ready")
    """
    from concurrent.futures import as_completed as _as_completed
    for future in _as_completed(futures):
        yield future.result()