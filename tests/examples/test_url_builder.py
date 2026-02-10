"""
Example: How to use URLBuilder

URLBuilder allows you to build API URLs without creating APIClient instances.
It shares cache with APIClient for optimal performance.
"""
from framework.api import URLBuilder, build_url
from framework.api import APIClient


def example_basic_usage():
    """Basic URLBuilder usage"""
    print("=" * 60)
    print("Example 1: Basic Usage")
    print("=" * 60)
    
    # Build URLs without creating APIClient instance
    url1 = URLBuilder.build('oauth2', 'signup')
    print(f"OAuth2 Signup URL: {url1}")
    
    url2 = URLBuilder.build('admin', 'users_2fa_enable')
    print(f"Admin 2FA URL: {url2}")
    
    url3 = URLBuilder.build('api', 'chat_messages')
    print(f"Chat Messages URL: {url3}")
    
    # Using shortcut function
    url4 = build_url('chime', 'create_room')
    print(f"Chime Create Room URL: {url4}")
    print()


def example_get_parts():
    """Get URL parts separately"""
    print("=" * 60)
    print("Example 2: Get URL Parts")
    print("=" * 60)
    
    # Get base URL
    base_url = URLBuilder.service_url('admin')
    print(f"Admin Base URL: {base_url}")
    
    # Get endpoint path
    path = URLBuilder.endpoint_path('admin', 'users_2fa_enable')
    print(f"Endpoint Path: {path}")
    
    # Combine manually if needed
    full_url = base_url + path
    print(f"Full URL: {full_url}")
    print()


def example_list_services_and_endpoints():
    """List available services and endpoints"""
    print("=" * 60)
    print("Example 3: List Services and Endpoints")
    print("=" * 60)
    
    # List all services
    services = URLBuilder.list_services()
    print(f"Available Services ({len(services)}): {services[:5]}...")
    
    # List endpoints for a specific service
    oauth2_endpoints = URLBuilder.list_endpoints('oauth2')
    print(f"\nOAuth2 Endpoints ({len(oauth2_endpoints)}):")
    for endpoint in oauth2_endpoints:
        print(f"  - {endpoint}")
    
    api_endpoints = URLBuilder.list_endpoints('api')
    print(f"\nAPI Endpoints ({len(api_endpoints)}): {api_endpoints[:10]}...")
    print()


def example_cache_info():
    """Check cache information"""
    print("=" * 60)
    print("Example 4: Cache Information")
    print("=" * 60)
    
    # Get cache statistics
    info = URLBuilder.cache_info()
    print(f"Cache Loaded: {info['loaded']}")
    print(f"Total Services: {info.get('services', 0)}")
    print(f"Total Endpoints: {info.get('total_endpoints', 0)}")
    
    if info['loaded']:
        print(f"\nServices: {info['service_names']}")
        print(f"\nEndpoints per service:")
        for service, count in info['endpoints_per_service'].items():
            print(f"  - {service}: {count} endpoints")
    print()


def example_shared_cache():
    """Demonstrate shared cache between URLBuilder and APIClient"""
    print("=" * 60)
    print("Example 5: Shared Cache with APIClient")
    print("=" * 60)
    
    # Clear cache first (for demo purposes)
    URLBuilder.clear_cache()
    
    print("Step 1: Build URL with URLBuilder (loads endpoint.yaml)")
    url1 = URLBuilder.build('oauth2', 'signup')
    print(f"  URL: {url1}")
    
    print("\nStep 2: Check cache")
    info = URLBuilder.cache_info()
    print(f"  Cache loaded: {info['loaded']}")
    print(f"  Total endpoints: {info['total_endpoints']}")
    
    print("\nStep 3: Create APIClient and use it (uses cached endpoints)")
    client = APIClient()
    url2 = client.oauth2.token.url
    print(f"  URL: {url2}")
    print("  ✓ No file I/O - used cached endpoints!")
    
    print("\nStep 4: Build another URL (still using cache)")
    url3 = URLBuilder.build('api', 'collections')
    print(f"  URL: {url3}")
    print("  ✓ endpoint.yaml only loaded ONCE!")
    print()


def example_use_in_auth_helper():
    """Example: How to use in auth_helper.py"""
    print("=" * 60)
    print("Example 6: Usage in auth_helper.py")
    print("=" * 60)
    
    print("BEFORE (need to create APIClient instance):")
    print("  _api_client = APIClient()")
    print("  url = _api_client.admin.users_2fa_enable.url")
    
    print("\nAFTER (no instance needed):")
    print("  from framework.api import URLBuilder")
    print("  url = URLBuilder.build('admin', 'users_2fa_enable')")
    
    # Demo
    url = URLBuilder.build('admin', 'users_2fa_enable')
    print(f"\n  Result: {url}")
    
    print("\nBenefits:")
    print("  ✓ No APIClient instance creation")
    print("  ✓ No Session object overhead")
    print("  ✓ Shared cache with APIClient")
    print("  ✓ Clean and simple")
    print()


if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "URLBuilder Examples" + " " * 23 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    try:
        example_basic_usage()
        example_get_parts()
        example_list_services_and_endpoints()
        example_cache_info()
        example_shared_cache()
        example_use_in_auth_helper()
        
        print("=" * 60)
        print("All examples completed successfully! ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
