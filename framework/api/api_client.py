# framework/api/api_client.py
from pathlib import Path

import requests
import yaml

from framework.api.helpers import auth_helper
from framework.consts.consts_common import UserRoles
from framework.core.config import ProjConfig
from framework.utils.logging_util import logger


class EndpointWrapper:
    """Wrapper cho một endpoint cụ thể"""
    
    def __init__(self, base_url, endpoint_path, session):
        self.base_url = base_url
        self.endpoint_path = endpoint_path
        self.session = session
        self.full_url = base_url + endpoint_path
    
    @property
    def url(self):
        """Lấy full URL của endpoint"""
        return self.full_url
    
    def build_url(self, path_params=None, query_params=None):
        """Build URL với params"""
        url = self.full_url
        
        if path_params:
            url = url.format(**path_params)
        
        if query_params:
            from urllib.parse import urlencode
            query_string = urlencode(query_params)
            url = f"{url}?{query_string}"
        
        return url
    
    def __str__(self):
        return self.full_url
    
    def __repr__(self):
        return f"EndpointWrapper(url='{self.full_url}')"
    
    def get(self, params=None, **kwargs):
        return self.session.get(self.full_url, params=params, **kwargs)
    
    def post(self, params=None, json=None, data=None, **kwargs):
        return self.session.post(self.full_url, params=params, json=json, data=data, **kwargs)
    
    def put(self, params=None, json=None, data=None, **kwargs):
        return self.session.put(self.full_url, params=params, json=json, data=data, **kwargs)
    
    def delete(self, params=None, **kwargs):
        return self.session.delete(self.full_url, params=params, **kwargs)
    
    def patch(self, params=None, json=None, data=None, **kwargs):
        return self.session.patch(self.full_url, params=params, json=json, data=data, **kwargs)
    
    def info(self):
        """Lấy thông tin chi tiết về endpoint"""
        return {
            'base_url': self.base_url,
            'endpoint_path': self.endpoint_path,
            'full_url': self.full_url,
        }


class ServiceClient:
    """Client for a specific API service với lazy loading endpoints"""
    
    # CLASS-LEVEL cache - share giữa tất cả instances
    _all_endpoints_cache = None  # Cache toàn bộ endpoints từ yaml
    _cache_lock = None  # Thread-safe lock
    
    def __init__(self, service_name, base_url, session):
        self.service_name = service_name
        self.base_url = base_url
        self.session = session
        
        # Instance-level: chỉ cache endpoints của service này
        self._endpoints = None
        self._endpoint_cache = {}
        
        # Khởi tạo lock nếu chưa có
        if ServiceClient._cache_lock is None:
            from threading import Lock
            ServiceClient._cache_lock = Lock()
    
    @classmethod
    def _load_all_endpoints(cls):
        """
        Load TẤT CẢ endpoints từ yaml - CHỈ 1 LẦN cho tất cả instances
        Thread-safe
        """
        # Khởi tạo lock nếu chưa có (thread-safe với check-lock-check pattern)
        if cls._cache_lock is None:
            from threading import Lock

            # Double-checked locking pattern (simplified - Python GIL makes this safe enough)
            cls._cache_lock = Lock()
        
        if cls._all_endpoints_cache is not None:
            return cls._all_endpoints_cache  # Đã load rồi
        
        with cls._cache_lock:
            # Double-check locking pattern
            if cls._all_endpoints_cache is not None:
                return cls._all_endpoints_cache
            
            endpoint_file = Path(__file__).parent.parent.parent / 'resources' / 'yaml' / 'endpoint.yaml'
            
            if not endpoint_file.exists():
                print(f"Warning: endpoint.yaml not found at {endpoint_file}")
                cls._all_endpoints_cache = {}
                return {}
            
            try:
                with open(endpoint_file, 'r') as f:
                    cls._all_endpoints_cache = yaml.safe_load(f) or {}
                print(f"✓ Loaded endpoints from {endpoint_file.name}")
            except Exception as e:
                print(f"Error loading endpoints: {e}")
                cls._all_endpoints_cache = {}
            
            return cls._all_endpoints_cache
    
    def _load_endpoints(self):
        """Load endpoints cho service này từ class-level cache"""
        if self._endpoints is not None:
            return  # Đã load cho instance này rồi
        
        # Load từ class-level cache (chỉ đọc file 1 lần cho tất cả instances)
        all_endpoints = self._load_all_endpoints()
        
        # Lấy endpoints của service này
        self._endpoints = all_endpoints.get(self.service_name, {})
        
        if not self._endpoints:
            print(f"Warning: No endpoints found for service '{self.service_name}'")
    
    def __getattr__(self, name):
        """Lazy load endpoint khi được gọi"""
        # Load endpoints nếu chưa load (từ cache)
        if self._endpoints is None:
            self._load_endpoints()
        
        # Check cache trước
        if name in self._endpoint_cache:
            return self._endpoint_cache[name]
        
        # Check trong endpoints
        if name in self._endpoints:
            endpoint_path = self._endpoints[name]
            wrapper = EndpointWrapper(self.base_url, endpoint_path, self.session)
            self._endpoint_cache[name] = wrapper
            return wrapper
        
        raise AttributeError(
            f"Service '{self.service_name}' has no endpoint '{name}'. "
            f"Available endpoints: {list(self._endpoints.keys()) if self._endpoints else '[]'}"
        )
    
    # Giữ methods trực tiếp cho flexibility
    def get(self, path="", params=None, **kwargs):
        url = self.base_url + path if path else self.base_url
        return self.session.get(url, params=params, **kwargs)

    def post(self, path="", params=None, json=None, data=None, **kwargs):
        url = self.base_url + path if path else self.base_url
        return self.session.post(url, params=params, json=json, data=data, **kwargs)

    def put(self, path="", params=None, json=None, data=None, **kwargs):
        url = self.base_url + path if path else self.base_url
        return self.session.put(url, params=params, json=json, data=data, **kwargs)

    def delete(self, path="", params=None, **kwargs):
        url = self.base_url + path if path else self.base_url
        return self.session.delete(url, params=params, **kwargs)
    
    @classmethod
    def clear_cache(cls):
        """Clear class-level cache - useful for testing"""
        with cls._cache_lock:
            cls._all_endpoints_cache = None
            logger.debug("✓ Endpoints cache cleared")


class APIClient:
    def __init__(
        self, headers=None, base_url=None, *, email=None, password=None, auto_login=True, 
        device_uid=None, app_id=None, fake=False, internal_group=None, is_2fa=False, is_web=False, is_existed=None, **kwargs):
        self.session = requests.Session()
        
        # KHÔNG load services sẵn, chỉ lưu URL configs
        self._service_urls = {}
        url_data = ProjConfig.get_config('base_url')
        
        for service_name, service_url in url_data.items():
            if isinstance(service_url, str) and service_url.startswith('http'):
                self._service_urls[service_name] = service_url
        
        # Cache services đã tạo
        self._services = {}
        self.base_url = base_url or ProjConfig.API_BASE_URL
        
        # Initialize attributes before login (so login can use them)
        self.fake = fake
        self.internal_group = internal_group
        self.is_2fa = is_2fa
        self.is_web = is_web
        self.is_existed = is_existed
        self.email = email or ProjConfig.get_config("user")
        self.password = password or ProjConfig.get_config("password")
        self.device_uid = device_uid or ProjConfig.get_config("device_uid")
        self.app_id = app_id or ProjConfig.get_config("app_id")
        
        if not headers and auto_login:
            self.headers, self.email = self.login(
                email=email,
                password=password,
                device_uid=device_uid,
                app_id=app_id,
                fake=fake,
                internal_group=internal_group,
                is_2fa=is_2fa,
                is_web=is_web,
                is_existed=is_existed,
                **kwargs,
            )
        else:
            self.headers = headers or auth_helper.headers_app(username=email)
            self.email = (
                email or self.headers.get("auto_request_id", "").split("-floauto.")[-1] + ProjConfig.get_config("domain") or self.email
            )
        
        # Update attributes with login results
        self.session.headers.update(self.headers)
        self.username = self.email.partition("@")[0]
        self.password = password or self.password
        self.device_uid = self.headers.get("device_uid", self.device_uid)
        self.app_id = self.headers.get("app_id", self.app_id)
        self.app = [k for k, v in ProjConfig.get_config("app_ids").items() if v == self.app_id][0]
        self.access_token = (self.headers, self.email)
        self.role = UserRoles.OWNER if "_mem" not in self.email else UserRoles.MEMBER
        self.is_member = self.role == UserRoles.MEMBER
    
    def login(self, email=None, password=None, device_uid=None, app_id=None, fake=False, internal_group=None, is_2fa=False, is_web=False, is_existed=None, **kwargs):
        """Login to the API"""
        _headers, _email = auth_helper.access_token(
            user=email or self.email,
            password=password or self.password,
            device_uid=device_uid or self.device_uid,
            app_id=app_id or self.app_id,
            fake=fake or self.fake,
            internal_group=internal_group or self.internal_group,
            is_2fa=is_2fa or self.is_2fa,
            is_web=is_web or self.is_web,
            is_existed=is_existed or self.is_existed,
            **kwargs,
        )
        return _headers, _email
    
    def __getattr__(self, name):
        """
        Lazy create service client khi được gọi
        Example: client.api → tạo ServiceClient cho 'api' service
        """
        # Check cache trước
        if name in self._services:
            return self._services[name]
        
        # Check xem service có URL không
        if name in self._service_urls:
            # Tạo ServiceClient (chưa load endpoints)
            service = ServiceClient(
                service_name=name,
                base_url=self._service_urls[name],
                session=self.session
            )
            
            # Cache lại
            self._services[name] = service
            return service
        
        raise AttributeError(
            f"'{type(self).__name__}' has no service '{name}'. "
            f"Available services: {list(self._service_urls.keys())}"
        )
    
    # Backward compatibility methods
    def get(self, path="", **kwargs):
        return self.session.get(self.base_url + path, **kwargs)

    def post(self, path="", **kwargs):
        return self.session.post(self.base_url + path, **kwargs)

    def put(self, path="", **kwargs):
        return self.session.put(self.base_url + path, **kwargs)

    def delete(self, path="", **kwargs):
        return self.session.delete(self.base_url + path, **kwargs)