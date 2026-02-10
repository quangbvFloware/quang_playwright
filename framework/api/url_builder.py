"""
URLBuilder - Build API URLs without creating APIClient instances
Shares cache with ServiceClient for optimal performance
"""
from framework.core.config import ProjConfig
from framework.utils.logging_util import logger


class URLBuilder:
    """
    Build URLs without creating APIClient instance
    Uses shared cache with ServiceClient - endpoint.yaml only loaded once
    """
    
    @classmethod
    def build(cls, service, endpoint):
        """
        Build full URL for a service endpoint
        
        Args:
            service: Service name (e.g., 'api', 'oauth2', 'admin', 'chime')
            endpoint: Endpoint name (e.g., 'chat_messages', 'signup', 'users_2fa_enable')
        
        Returns:
            Full URL string
        
        Example:
            >>> URLBuilder.build('admin', 'users_2fa_enable')
            'https://admin-api.k8s.flostage.com/users/2fa/enable'
            
            >>> URLBuilder.build('oauth2', 'signup')
            'https://oauth2-api.k8s.flostage.com/signup'
        """
        # Lấy service URL từ config
        url_data = ProjConfig.get_config('base_url')
        service_url = url_data.get(service)
        
        if not service_url:
            available = [k for k, v in url_data.items() if isinstance(v, str) and v.startswith('http')]
            raise ValueError(
                f"Service '{service}' not found in config. "
                f"Available services: {available}"
            )
        
        # Sử dụng shared cache của ServiceClient
        # Import ở đây để tránh circular import
        from framework.api.api_client import ServiceClient
        endpoints = ServiceClient._load_all_endpoints()
        
        endpoint_path = endpoints.get(service, {}).get(endpoint) if endpoint != '' else ''
        
        if endpoint != '' and not endpoint_path:
            available_endpoints = list(endpoints.get(service, {}).keys())
            raise ValueError(
                f"Endpoint '{endpoint}' not found for service '{service}'. "
                f"Available endpoints: {available_endpoints[:10]}"  # Show first 10
            )
        
        return service_url + endpoint_path
    
    @classmethod
    def service_url(cls, service):
        """
        Get base URL of a service
        
        Args:
            service: Service name (e.g., 'api', 'oauth2', 'admin')
        
        Returns:
            Base URL string
        
        Example:
            >>> URLBuilder.service_url('admin')
            'https://admin-api.k8s.flostage.com'
        """
        url_data = ProjConfig.get_config('base_url')
        service_url = url_data.get(service)
        
        if not service_url:
            raise ValueError(f"Service '{service}' not found in config")
        
        return service_url
    
    @classmethod
    def endpoint_path(cls, service, endpoint):
        """
        Get endpoint path (without base URL)
        
        Args:
            service: Service name
            endpoint: Endpoint name
        
        Returns:
            Endpoint path string
        
        Example:
            >>> URLBuilder.endpoint_path('admin', 'users_2fa_enable')
            '/users/2fa/enable'
        """
        from framework.api.api_client import ServiceClient
        endpoints = ServiceClient._load_all_endpoints()
        
        endpoint_path = endpoints.get(service, {}).get(endpoint)
        
        if not endpoint_path:
            raise ValueError(
                f"Endpoint '{endpoint}' not found for service '{service}'"
            )
        
        return endpoint_path
    
    @classmethod
    def list_services(cls):
        """
        List all available services
        
        Returns:
            List of service names
        
        Example:
            >>> URLBuilder.list_services()
            ['api', 'oauth2', 'admin', 'chime', 'web', ...]
        """
        url_data = ProjConfig.get_config('base_url')
        return [
            k for k, v in url_data.items() 
            if isinstance(v, str) and v.startswith('http')
        ]
    
    @classmethod
    def list_endpoints(cls, service):
        """
        List all endpoints for a specific service
        
        Args:
            service: Service name
        
        Returns:
            List of endpoint names
        
        Example:
            >>> URLBuilder.list_endpoints('oauth2')
            ['signup', 'token', 'checkemail', 'refresh', ...]
        """
        from framework.api.api_client import ServiceClient
        endpoints = ServiceClient._load_all_endpoints()
        
        service_endpoints = endpoints.get(service, {})
        
        if not service_endpoints:
            raise ValueError(
                f"No endpoints found for service '{service}'. "
                f"Available services: {list(endpoints.keys())}"
            )
        
        return list(service_endpoints.keys())
    
    @classmethod
    def cache_info(cls):
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache information
        
        Example:
            >>> URLBuilder.cache_info()
            {
                'loaded': True,
                'services': 10,
                'service_names': ['api', 'oauth2', ...],
                'total_endpoints': 150,
                'endpoints_per_service': {'api': 100, 'oauth2': 10, ...}
            }
        """
        from framework.api.api_client import ServiceClient
        
        cache = ServiceClient._all_endpoints_cache
        
        if cache is None:
            return {
                'loaded': False,
                'services': 0,
                'total_endpoints': 0
            }
        
        total_endpoints = sum(len(endpoints) for endpoints in cache.values())
        
        return {
            'loaded': True,
            'services': len(cache),
            'service_names': list(cache.keys()),
            'total_endpoints': total_endpoints,
            'endpoints_per_service': {
                service: len(endpoints) 
                for service, endpoints in cache.items()
            }
        }
    
    @classmethod
    def clear_cache(cls):
        """
        Clear shared endpoints cache
        Useful for testing or forcing reload
        
        Example:
            >>> URLBuilder.clear_cache()
            ✓ Endpoints cache cleared
        """
        from framework.api.api_client import ServiceClient
        ServiceClient._all_endpoints_cache = None
        logger.debug("✓ Endpoints cache cleared")


# Convenience function
def build_url(service, endpoint):
    """
    Shortcut function to build URL
    
    Example:
        >>> from framework.api.url_builder import build_url
        >>> url = build_url('oauth2', 'signup')
    """
    return URLBuilder.build(service, endpoint)
