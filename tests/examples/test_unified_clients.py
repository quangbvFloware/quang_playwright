"""
Example: How to use unified client fixtures with DotDict auto-execution

All client fixtures follow the same pattern:
- owner: Main/first instance
- member: Second instance  
- member_2: Third instance

DotDict Magic:
- When you access an attribute (e.g., api_clients.owner)
- DotDict automatically executes the 'function' with other params as kwargs
- Returns the client instance directly

Available fixtures:
- api_clients
- web_clients
- mac_clients
- iphone_clients
- ipad_clients
"""
import pytest
from framework.consts.consts_common import APIServiceType
from framework.setup_client import wait_all


# ========================================
# Example 1: Single Client - DotDict Auto-Execution
# ========================================

def test_api_single(api_clients):
    """Test with single API client - DotDict magic!"""
    
    # Just access .owner - DotDict automatically executes setup_api_client()!
    owner = api_clients.owner
    
    # owner is now an APIClient instance
    response = owner.api.collections.get()
    assert response.status_code == 200
    
    print("✓ Single client test passed")


# ========================================
# Example 2: Multiple Clients - Automatic Parallel Execution
# ========================================

def test_api_collaboration(api_clients):
    """Test with 3 API clients - all start in parallel automatically!"""
    
    # Just access all 3 - DotDict executes all functions in parallel threads!
    owner = api_clients.owner      # ← Starts thread 1
    member = api_clients.member    # ← Starts thread 2
    member_2 = api_clients.member_2  # ← Starts thread 3
    
    print("All 3 API clients starting in background (parallel)...")
    
    # When you use them, they'll wait if not ready yet
    # Test collaboration
    response = owner.api.workspaces.post(json={'name': 'Team Workspace'})
    assert response.status_code == 200
    
    response = member.api.workspaces.get()
    assert response.status_code == 200
    
    response = member_2.api.workspaces.get()
    assert response.status_code == 200
    
    print("✓ All 3 clients worked in parallel!")


# ========================================
# Example 3: Web Clients - Automatic Parallel
# ========================================

def test_web_chat(web_clients):
    """Test chat with 3 web browsers - parallel automatically!"""
    
    # Access all 3 - DotDict starts all browsers in parallel!
    owner = web_clients.owner      # ← Browser 1 starts
    member = web_clients.member    # ← Browser 2 starts
    member_2 = web_clients.member_2  # ← Browser 3 starts
    
    print("3 browsers starting in parallel...")
    
    # Use them - they wait if not ready yet
    owner.channel_page.create_channel("Group Chat")
    member.channel_page.join_channel("Group Chat")
    member_2.channel_page.join_channel("Group Chat")
    
    owner.channel_page.send_message("Hello everyone!")
    
    print("✓ 3 browsers worked together!")


# ========================================
# Example 4: iPhone + iPad - Cross-Device
# ========================================

def test_iphone_ipad_sync(iphone_clients, ipad_clients):
    """Test sync between iPhone and iPad - DotDict magic!"""
    
    # Access both - start in parallel automatically
    iphone = iphone_clients.owner  # ← iPhone starts
    ipad = ipad_clients.owner      # ← iPad starts
    
    print("iPhone and iPad starting in parallel...")
    
    # Test sync between devices
    iphone.find_element('create_note').click()
    iphone.send_keys('Note from iPhone')
    
    # Should sync to iPad
    ipad.pull_to_refresh()
    note = ipad.find_element('note_text')
    assert note.text == 'Note from iPhone'
    
    print("✓ iPhone and iPad synced!")


# ========================================
# Example 5: All 15 Clients - Maximum Parallelism
# ========================================

def test_all_platforms(api_clients, web_clients, mac_clients, iphone_clients, ipad_clients):
    """Ultimate test - 15 clients across 5 platforms, all parallel!"""
    
    print("Starting 15 clients across 5 platforms...")
    
    # Just access all attributes - all start in parallel automatically!
    # API (3)
    api_owner = api_clients.owner
    api_member = api_clients.member
    api_member_2 = api_clients.member_2
    
    # Web (3)
    web_owner = web_clients.owner
    web_member = web_clients.member
    web_member_2 = web_clients.member_2
    
    # Mac (3)
    mac_owner = mac_clients.owner
    mac_member = mac_clients.member
    mac_member_2 = mac_clients.member_2
    
    # iPhone (3)
    iphone_owner = iphone_clients.owner
    iphone_member = iphone_clients.member
    iphone_member_2 = iphone_clients.member_2
    
    # iPad (3)
    ipad_owner = ipad_clients.owner
    ipad_member = ipad_clients.member
    ipad_member_2 = ipad_clients.member_2
    
    print("All 15 clients started in parallel!")
    
    # Use any client - it will wait if not ready yet
    api_owner.api.notifications.post(json={'message': 'Cross-platform test'})
    web_owner.open('/notifications')
    
    print("✓ All 15 clients working!")


# ========================================
# Example 6: Backward Compatibility
# ========================================

def test_legacy_mac(mac):
    """Legacy fixture still works"""
    mac.click_element('button')


def test_legacy_ios(ios):
    """Legacy parameterized fixture still works"""
    # Will run twice: once for iPhone, once for iPad
    ios.find_element('app_icon').click()


# ========================================
# Example 9: Helper Function Pattern
# ========================================

def get_all_clients_for_role(role, *client_fixtures):
    """
    Get clients from multiple fixtures for same role
    
    Example:
        api, web = get_all_clients_for_role('owner', api_clients, web_clients)
    """
    return tuple(fixture[role] for fixture in client_fixtures)


def test_with_helper(api_clients, web_clients):
    """Use helper function for cleaner code"""
    
    # Get API and Web clients for owner role
    api_owner, web_owner = get_all_clients_for_role('owner', api_clients, web_clients)
    
    # Both started in parallel, use directly
    api_owner.api.collections.post(json={'name': 'Test'})
    web_owner.open('/collections')
    
    print("✓ Helper function works!")
