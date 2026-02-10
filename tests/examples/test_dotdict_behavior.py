"""
Test to verify DotDict auto-execution behavior with client fixtures
"""
import pytest
from framework.consts.consts_common import APIServiceType


def test_api_clients_dotdict_behavior(api_clients):
    """Verify DotDict auto-executes setup_api_client when accessing attributes"""
    
    # Test 1: First access should execute function and return APIClient instance
    print("\n=== Test 1: First access to api_clients.owner ===")
    owner = api_clients.owner
    
    # Verify it's an APIClient instance (not a dict, not a Future)
    from framework.api.api_client import APIClient
    assert isinstance(owner, APIClient), f"Expected APIClient, got {type(owner)}"
    print(f"✓ owner is APIClient instance: {type(owner)}")
    
    # Verify we can use it directly
    assert hasattr(owner, 'session'), "APIClient should have session attribute"
    print("✓ APIClient has session attribute")
    
    # Test 2: Second access should return cached instance (same object)
    print("\n=== Test 2: Second access (should be cached) ===")
    owner2 = api_clients.owner
    assert owner is owner2, "Second access should return same cached instance"
    print(f"✓ Same instance cached: id(owner)={id(owner)}, id(owner2)={id(owner2)}")
    
    # Test 3: Access member - should create new independent instance
    print("\n=== Test 3: Access different attribute (member) ===")
    member = api_clients.member
    assert isinstance(member, APIClient), f"Expected APIClient, got {type(member)}"
    assert owner is not member, "member should be different instance than owner"
    print(f"✓ member is independent APIClient instance")
    
    print("\n=== All DotDict behavior tests passed! ===")


def test_multiple_clients_parallel(api_clients):
    """Verify multiple clients can be created in parallel"""
    
    print("\n=== Test: Parallel client creation ===")
    
    # Access all 3 - they should all start in parallel
    owner = api_clients.owner
    member = api_clients.member
    member_2 = api_clients.member_2
    
    # Verify all are APIClient instances
    from framework.api.api_client import APIClient
    assert isinstance(owner, APIClient)
    assert isinstance(member, APIClient)
    assert isinstance(member_2, APIClient)
    
    # Verify all are different instances
    assert owner is not member
    assert owner is not member_2
    assert member is not member_2
    
    print("✓ All 3 clients are independent APIClient instances")
    print(f"  owner id:    {id(owner)}")
    print(f"  member id:   {id(member)}")
    print(f"  member_2 id: {id(member_2)}")
    
    print("\n=== Parallel creation test passed! ===")


def test_selective_access(api_clients):
    """Verify only accessed attributes are created (lazy loading)"""
    
    print("\n=== Test: Selective access (lazy loading) ===")
    
    # Only access owner
    owner = api_clients.owner
    
    from framework.api.api_client import APIClient
    assert isinstance(owner, APIClient)
    print("✓ owner created")
    
    # Check internal state - member should still be a dict (not executed yet)
    # Access dict directly without triggering __getattr__
    member_config = dict.__getitem__(api_clients, 'member')
    assert isinstance(member_config, dict), "member should still be dict config"
    assert 'function' in member_config, "member config should have function key"
    print("✓ member NOT created yet (still a dict config)")
    
    # Now access member - should trigger execution
    member = api_clients.member
    assert isinstance(member, APIClient)
    print("✓ member created on first access")
    
    # Check again - should now be APIClient (replaced in cache)
    member_cached = dict.__getitem__(api_clients, 'member')
    assert isinstance(member_cached, APIClient)
    print("✓ member is now cached as APIClient instance")
    
    print("\n=== Selective access test passed! ===")


def test_dotdict_with_different_client_types(api_clients, web_clients):
    """Verify DotDict works consistently across different client types"""
    
    print("\n=== Test: DotDict consistency across client types ===")
    
    # API client
    api_owner = api_clients.owner
    from framework.api.api_client import APIClient
    assert isinstance(api_owner, APIClient)
    print(f"✓ api_clients.owner: {type(api_owner).__name__}")
    
    # Web client
    web_owner = web_clients.owner
    from framework.web.web_client import WebClient
    assert isinstance(web_owner, WebClient)
    print(f"✓ web_clients.owner: {type(web_owner).__name__}")
    
    # Both should be cached on second access
    api_owner2 = api_clients.owner
    web_owner2 = web_clients.owner
    assert api_owner is api_owner2
    assert web_owner is web_owner2
    print("✓ Both client types cache correctly")
    
    print("\n=== Consistency test passed! ===")


if __name__ == '__main__':
    """Run with: pytest tests/test_dotdict_behavior.py -v -s"""
    pytest.main([__file__, '-v', '-s'])
