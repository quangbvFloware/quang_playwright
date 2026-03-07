"""
Test to verify parallel_get functions work correctly

This demonstrates that parallel_get truly starts clients in parallel,
not sequentially like normal DotDict access.
"""
import time
import pytest
from framework.utils import parallel_get, parallel_get_all, DotDict
from framework.setup_client import ClientExecutor


def slow_client_factory(delay):
    """Factory that creates slow client setup functions using ThreadPoolExecutor"""
    def setup(user, password, delay=delay):
        """Setup function that returns Future (runs in thread pool)"""
        def _create_slow():
            """Internal function that simulates slow creation"""
            time.sleep(delay)
            
            class MockClient:
                def __init__(self):
                    self.user = user
                    self.created_at = time.time()
            
            return MockClient()
        
        # Submit to thread pool and return Future immediately
        return ClientExecutor.submit(_create_slow)
    
    return setup


def test_sequential_access_is_slow():
    """Baseline: Normal DotDict access is sequential"""
    print("\n" + "="*60)
    print("TEST 1: Sequential Access (Normal DotDict)")
    print("="*60)
    
    clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='owner@test.com',
            password='pass'
        ),
        member=dict(
            function=slow_client_factory(0.5),
            user='member@test.com',
            password='pass'
        )
    )
    
    start = time.time()
    
    # Normal access - sequential (blocking)
    owner = clients.owner    # Wait 0.5s
    member = clients.member  # Wait 0.5s
    
    elapsed = time.time() - start
    
    print(f"✓ Owner created: {owner.user}")
    print(f"✓ Member created: {member.user}")
    print(f"⏱  Total time: {elapsed:.2f}s")
    print(f"   Expected: ~1.0s (0.5s + 0.5s sequential)")
    
    assert elapsed >= 0.9, "Should take ~1.0s for sequential"
    print("✓ Sequential access verified")


def test_parallel_get_is_fast():
    """parallel_get starts clients truly in parallel"""
    print("\n" + "="*60)
    print("TEST 2: Parallel Access (parallel_get)")
    print("="*60)
    
    clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='owner@test.com',
            password='pass'
        ),
        member=dict(
            function=slow_client_factory(0.5),
            user='member@test.com',
            password='pass'
        )
    )
    
    start = time.time()
    
    # Parallel access - both start simultaneously
    owner, member = parallel_get_all(clients, 'owner', 'member')
    
    elapsed = time.time() - start
    
    print(f"✓ Owner created: {owner.user}")
    print(f"✓ Member created: {member.user}")
    print(f"⏱  Total time: {elapsed:.2f}s")
    print(f"   Expected: ~0.5s (both in parallel)")
    
    assert elapsed < 0.8, "Should take ~0.5s for parallel (not 1.0s)"
    print("✓ Parallel execution verified - 2x faster!")


def test_parallel_get_cross_fixtures():
    """parallel_get works across different fixtures"""
    print("\n" + "="*60)
    print("TEST 3: Cross-Fixture Parallel (API + Web)")
    print("="*60)
    
    api_clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='api@test.com',
            password='pass'
        )
    )
    
    web_clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='web@test.com',
            password='pass'
        )
    )
    
    start = time.time()
    
    # Start API and Web clients in parallel
    api_owner, web_owner = parallel_get(
        (api_clients, 'owner'),
        (web_clients, 'owner')
    )
    
    elapsed = time.time() - start
    
    print(f"✓ API client created: {api_owner.user}")
    print(f"✓ Web client created: {web_owner.user}")
    print(f"⏱  Total time: {elapsed:.2f}s")
    print(f"   Expected: ~0.5s (both in parallel)")
    
    assert elapsed < 0.8, "Should take ~0.5s for parallel"
    print("✓ Cross-fixture parallel verified!")


def test_parallel_get_multiple_roles():
    """parallel_get with different roles across fixtures"""
    print("\n" + "="*60)
    print("TEST 4: Multiple Roles Parallel")
    print("="*60)
    
    api_clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='api_owner@test.com',
            password='pass'
        ),
        member=dict(
            function=slow_client_factory(0.5),
            user='api_member@test.com',
            password='pass'
        )
    )
    
    web_clients = DotDict(
        owner=dict(
            function=slow_client_factory(0.5),
            user='web_owner@test.com',
            password='pass'
        )
    )
    
    start = time.time()
    
    # Start 3 clients in parallel (different fixtures, different roles)
    api_owner, api_member, web_owner = parallel_get(
        (api_clients, 'owner'),
        (api_clients, 'member'),
        (web_clients, 'owner')
    )
    
    elapsed = time.time() - start
    
    print(f"✓ API owner: {api_owner.user}")
    print(f"✓ API member: {api_member.user}")
    print(f"✓ Web owner: {web_owner.user}")
    print(f"⏱  Total time: {elapsed:.2f}s")
    print(f"   Expected: ~0.5s (all 3 in parallel)")
    
    # Sequential would be 1.5s (0.5 * 3)
    # Parallel should be ~0.5s
    assert elapsed < 0.8, "Should take ~0.5s for parallel (not 1.5s)"
    print("✓ Multiple roles parallel verified - 3x faster!")


def test_parallel_get_caching():
    """Verify parallel_get caches results back to DotDict"""
    print("\n" + "="*60)
    print("TEST 5: Caching Verification")
    print("="*60)
    
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
    
    # First parallel_get
    owner1, member1 = parallel_get_all(clients, 'owner', 'member')
    assert call_count['owner'] == 1
    assert call_count['member'] == 1
    print("✓ First call: both clients created")
    
    # Second access via normal DotDict
    owner2 = clients.owner
    member2 = clients.member
    assert call_count['owner'] == 1  # Still 1, not 2
    assert call_count['member'] == 1  # Still 1, not 2
    print("✓ Second call: returned cached (not recreated)")
    
    # Same instances
    assert owner1 is owner2
    assert member1 is member2
    print("✓ Same instances confirmed")


def test_comparison_sequential_vs_parallel():
    """Side-by-side comparison"""
    print("\n" + "="*60)
    print("TEST 6: Sequential vs Parallel Comparison")
    print("="*60)
    
    # Sequential test
    clients_seq = DotDict(
        client1=dict(function=slow_client_factory(0.3), user='1', password='p'),
        client2=dict(function=slow_client_factory(0.3), user='2', password='p'),
        client3=dict(function=slow_client_factory(0.3), user='3', password='p'),
    )
    
    start_seq = time.time()
    c1 = clients_seq.client1
    c2 = clients_seq.client2
    c3 = clients_seq.client3
    time_seq = time.time() - start_seq
    
    print(f"[Sequential] 3 clients: {time_seq:.2f}s (~0.9s expected)")
    
    # Parallel test
    clients_par = DotDict(
        client1=dict(function=slow_client_factory(0.3), user='1', password='p'),
        client2=dict(function=slow_client_factory(0.3), user='2', password='p'),
        client3=dict(function=slow_client_factory(0.3), user='3', password='p'),
    )
    
    start_par = time.time()
    c1, c2, c3 = parallel_get_all(clients_par, 'client1', 'client2', 'client3')
    time_par = time.time() - start_par
    
    print(f"[Parallel]   3 clients: {time_par:.2f}s (~0.3s expected)")
    
    speedup = time_seq / time_par
    print(f"\n✨ Speedup: {speedup:.1f}x faster with parallel_get!")
    
    assert speedup > 2.0, "Should be at least 2x faster"


if __name__ == '__main__':
    """Run with: pytest tests/test_parallel_get.py -v -s"""
    pytest.main([__file__, '-v', '-s'])
