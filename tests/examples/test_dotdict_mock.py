"""
Test to verify DotDict auto-execution behavior WITHOUT needing real API setup
"""
import pytest
from concurrent.futures import Future
from framework.utils import DotDict


def mock_setup_client(user: str, password: str, **kwargs):
    """Mock setup function that returns a mock client"""
    class MockClient:
        def __init__(self, user, password):
            self.user = user
            self.password = password
            self.session = "mock_session"
    
    return MockClient(user, password)


def test_dotdict_executes_function():
    """Verify DotDict auto-executes function when accessing attribute"""
    
    # Setup DotDict with mock function
    clients = DotDict(
        owner=dict(
            function=mock_setup_client,
            user='test@test.com',
            password='pass123'
        )
    )
    
    # Access owner - should execute function
    owner = clients.owner
    
    # Verify it's a MockClient instance (not dict, not Future)
    assert hasattr(owner, 'user'), "Should return MockClient instance"
    assert owner.user == 'test@test.com'
    assert owner.password == 'pass123'
    print("✓ DotDict executed function and returned client instance")


def test_dotdict_caches_result():
    """Verify DotDict caches the result"""
    
    clients = DotDict(
        owner=dict(
            function=mock_setup_client,
            user='test@test.com',
            password='pass123'
        )
    )
    
    # First access
    owner1 = clients.owner
    
    # Second access - should return cached instance
    owner2 = clients.owner
    
    # Should be same object
    assert owner1 is owner2
    print(f"✓ DotDict caches result: id(owner1)={id(owner1)}, id(owner2)={id(owner2)}")


def test_dotdict_handles_future():
    """Verify DotDict auto-calls .result() on Future"""
    from concurrent.futures import ThreadPoolExecutor
    
    def setup_in_thread(user, password):
        """Function that runs in thread"""
        import time
        time.sleep(0.1)  # Simulate work
        class MockClient:
            def __init__(self):
                self.user = user
                self.password = password
        return MockClient()
    
    # Create a function that returns Future
    def setup_client_async(user, password):
        executor = ThreadPoolExecutor(max_workers=1)
        future = executor.submit(setup_in_thread, user, password)
        executor.shutdown(wait=False)
        return future
    
    clients = DotDict(
        owner=dict(
            function=setup_client_async,
            user='test@test.com',
            password='pass123'
        )
    )
    
    # Access owner - DotDict should handle Future automatically
    owner = clients.owner
    
    # Should be MockClient instance, not Future
    assert not isinstance(owner, Future), "DotDict should call .result() on Future"
    assert hasattr(owner, 'user'), "Should return actual client instance"
    assert owner.user == 'test@test.com'
    print("✓ DotDict handles Future correctly by calling .result()")


def test_dotdict_lazy_loading():
    """Verify DotDict only creates clients when accessed"""
    
    call_count = {'owner': 0, 'member': 0}
    
    def counting_setup(user, password, client_type):
        call_count[client_type] += 1
        class MockClient:
            def __init__(self):
                self.user = user
        return MockClient()
    
    clients = DotDict(
        owner=dict(
            function=counting_setup,
            user='owner@test.com',
            password='pass',
            client_type='owner'
        ),
        member=dict(
            function=counting_setup,
            user='member@test.com',
            password='pass',
            client_type='member'
        )
    )
    
    # Initially, no calls
    assert call_count['owner'] == 0
    assert call_count['member'] == 0
    
    # Access only owner
    owner = clients.owner
    
    # Only owner should be created
    assert call_count['owner'] == 1
    assert call_count['member'] == 0
    print("✓ DotDict lazy loading: member not created when not accessed")
    
    # Access member now
    member = clients.member
    
    # Now member created
    assert call_count['member'] == 1
    print("✓ DotDict creates on first access")
    
    # Access owner again - should not recreate
    owner2 = clients.owner
    assert call_count['owner'] == 1  # Still 1, not 2
    print("✓ DotDict doesn't recreate on subsequent access")


def test_dotdict_multiple_independent_instances():
    """Verify accessing multiple attributes creates independent instances"""
    
    clients = DotDict(
        owner=dict(
            function=mock_setup_client,
            user='owner@test.com',
            password='pass'
        ),
        member=dict(
            function=mock_setup_client,
            user='member@test.com',
            password='pass'
        ),
        member_2=dict(
            function=mock_setup_client,
            user='member2@test.com',
            password='pass'
        )
    )
    
    # Access all 3
    owner = clients.owner
    member = clients.member
    member_2 = clients.member_2
    
    # All should be different instances
    assert owner is not member
    assert owner is not member_2
    assert member is not member_2
    
    # Each should have correct user
    assert owner.user == 'owner@test.com'
    assert member.user == 'member@test.com'
    assert member_2.user == 'member2@test.com'
    
    print("✓ All 3 clients are independent instances with correct data")


def test_dotdict_error_handling():
    """Verify DotDict handles function errors gracefully"""
    
    def failing_setup(user, password):
        raise ValueError("Setup failed!")
    
    clients = DotDict(
        owner=dict(
            function=failing_setup,
            user='test@test.com',
            password='pass'
        )
    )
    
    # Access should NOT raise - DotDict catches and returns dict
    owner = clients.owner
    
    # Should fallback to DotDict (converted dict)
    assert isinstance(owner, DotDict)
    assert 'function' in owner
    print("✓ DotDict handles errors gracefully by returning dict/DotDict")


if __name__ == '__main__':
    """Run with: pytest tests/test_dotdict_mock.py -v -s"""
    pytest.main([__file__, '-v', '-s'])
