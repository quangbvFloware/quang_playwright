# Unified Client Fixtures - User Guide

## 📋 Overview

All client fixtures in `tests/conftest.py` follow a unified pattern with **3 instances per type**:
- `owner`: Primary instance (main user or device 1)
- `member`: Secondary instance (member 1 or device 2)
- `member_2`: Tertiary instance (member 2 or device 3)

**Important**: All fixtures use `DotDict` which **automatically executes** the `function` keyword when accessing an attribute. This means:
- `api_clients.owner` → Automatically calls `setup_api_client()` and returns the client
- No need to call `.function()` manually
- Parameters are pre-configured in the fixture

## 🎯 Available Fixtures

### 1. **api_clients**
API clients for testing backend services

```python
def test_api(api_clients):
    # Simply access .owner - DotDict auto-executes setup_api_client()
    owner = api_clients.owner
    
    # owner is now an APIClient instance, use it directly!
    response = owner.api.collections.get()
    assert response.status_code == 200
```

### 2. **web_clients**
Web browser clients for UI testing

```python
def test_web(web_clients):
    # Access .owner - DotDict auto-executes setup_web_client()
    owner = web_clients.owner
    
    # owner is now a WebClient instance
    owner.open('/dashboard')
    owner.channel_page.create_channel("Test")
```

### 3. **mac_clients**
Mac automation clients

```python
def test_mac(mac_clients):
    # Access .owner - DotDict auto-executes setup_mac_client()
    owner = mac_clients.owner
    
    # owner is now a MacDriver instance
    owner.click_element('button')
```

### 4. **iphone_clients**
iPhone automation clients (all instances are iPhones)

```python
def test_iphone(iphone_clients):
    # Access .owner - DotDict auto-executes setup_ios_client()
    owner = iphone_clients.owner
    
    # owner is now an AppiumDriver instance
    owner.find_element('app_icon').click()
```

### 5. **ipad_clients**
iPad automation clients (all instances are iPads)

```python
def test_ipad(ipad_clients):
    # Access .owner - DotDict auto-executes setup_ios_client()
    owner = ipad_clients.owner
    
    # owner is now an AppiumDriver instance
    owner.find_element('app_icon').click()
```

## ⚡ Parallel Execution

DotDict executes functions **lazily** - only when you access the attribute. This enables parallel execution:

```python
def test_parallel(api_clients):
    # These execute in PARALLEL (lazy evaluation)
    # Just access the attributes - functions start in background threads
    owner = api_clients.owner      # ← Starts setup_api_client() in thread 1
    member = api_clients.member    # ← Starts setup_api_client() in thread 2
    member_2 = api_clients.member_2  # ← Starts setup_api_client() in thread 3
    
    # Functions are running in parallel now!
    # When you use the clients, they'll wait if not ready yet
    
    # Test collaboration
    owner.api.workspaces.post(json={'name': 'Team'})
    member.api.workspaces.get()
    member_2.api.workspaces.get()
```

## 📊 Fixture Structure

Each fixture returns a `DotDict` with this structure:

```python
{
    'owner': {
        'function': setup_xxx_client,  # Function to execute
        'username': 'user@example.com', # (API/Web only)
        'password': 'password123',      # (API/Web only)
        'service_type': APIServiceType.API,  # (API only)
        'headless': False,              # (Web only)
        'device_type': 'iphone',        # (iPhone/iPad only)
        'device_name': 'iPad Pro',      # (iPad only)
        'bundle_id': 'com.app',         # (Mac only)
        'caps_file': 'ios_caps.json',  # (Mac/iOS only)
        # ... other parameters are passed to setup function
    },
    'member': { ... },
    'member_2': { ... }
}
```

**When accessed**: `api_clients.owner` → DotDict calls `setup_api_client(**params)` → Returns client instance

## 🎭 Usage Patterns

### Pattern 1: Single Client (Simplest)

```python
def test_simple(api_clients):
    # Just access the attribute!
    owner = api_clients.owner
    
    # owner is APIClient instance
    response = owner.api.collections.get()
    assert response.status_code == 200
```

### Pattern 2: Multiple Clients (Automatic Parallel)

```python
def test_parallel(web_clients):
    # Access all 3 - they start in parallel automatically!
    owner = web_clients.owner      # Thread 1 starts
    member = web_clients.member    # Thread 2 starts
    member_2 = web_clients.member_2  # Thread 3 starts
    
    # All 3 browsers are loading in parallel now
    # Use them - will wait if not ready yet
    owner.channel_page.create_channel("Test")
    member.channel_page.join_channel("Test")
    member_2.channel_page.join_channel("Test")
```

### Pattern 3: Cross-Platform

```python
def test_cross_platform(api_clients, web_clients, iphone_clients):
    # Start clients on 3 different platforms - all in parallel!
    api = api_clients.owner
    web = web_clients.owner
    iphone = iphone_clients.owner
    
    # All 3 platforms starting in parallel automatically
    
    # Cross-platform test
    api.api.notifications.post(json={'message': 'Test'})
    web.open('/notifications')
    # iPhone app should also receive notification
```

### Pattern 4: All 15 Clients (Maximum Parallel)

```python
def test_massive(api_clients, web_clients, mac_clients, iphone_clients, ipad_clients):
    """Use all 15 clients - all start in parallel automatically!"""
    
    # Just access all attributes - all start immediately
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
    
    print("All 15 clients starting in parallel!")
    
    # Use any client - it will wait if not ready yet
    api_owner.api.notifications.post(json={'message': 'Test'})
```

### Pattern 5: Selective Usage

```python
def test_only_owner_and_member(api_clients):
    """Only use 2 out of 3 clients"""
    
    # Only access what you need - member_2 won't be created
    owner = api_clients.owner    # Created
    member = api_clients.member  # Created
    # member_2 is NOT accessed, so NOT created (efficient!)
    
    owner.api.workspaces.post(json={'name': 'Shared'})
    member.api.workspaces.get()
```

## 🔄 How DotDict Magic Works

```python
# Step-by-step breakdown
api_clients = DotDict(
    owner=dict(
        function=setup_api_client,
        username='test@test.com',
        password='pass',
        service_type=APIServiceType.API
    )
)

# When you access:
owner = api_clients.owner

# Behind the scenes:
# 1. __getitem__('owner') is called
# 2. _call_func() detects 'function' key
# 3. Extracts all other keys as kwargs: {username='test@test.com', password='pass', ...}
# 4. Calls: setup_api_client(username='test@test.com', password='pass', service_type=...)
# 5. Returns result (APIClient instance)
# 6. Replaces dict with result: api_clients['owner'] = <APIClient instance>
# 7. Future accesses return the cached client
```

## ⚙️ Configuration

### API Clients Structure

```python
@pytest.fixture(scope="session")
def api_clients(proj_config):
    return DotDict(
        owner=dict(
            function=setup_api_client,
            username=proj_config["user"],
            password=proj_config["password"],
            service_type=APIServiceType.API
        ),
        # All params except 'function' are passed to setup_api_client()
    )
```

### Web Clients Structure

```python
@pytest.fixture(scope="session")
def web_clients(proj_config, runtime_profile):
    return DotDict(
        owner=dict(
            function=setup_web_client,
            username=proj_config["user"],
            password=proj_config["password"],
            headless=runtime_profile.get('headless', False)
        ),
        # All params except 'function' are passed to setup_web_client()
    )
```

## 📈 Performance Benefits

### Lazy + Parallel Execution:
```python
def test_performance(api_clients):
    # All 3 start in parallel when accessed
    owner = api_clients.owner      # Start thread 1 (non-blocking)
    member = api_clients.member    # Start thread 2 (non-blocking)
    member_2 = api_clients.member_2  # Start thread 3 (non-blocking)
    
    # Total time: max(5s, 5s, 5s) = ~5s (parallel)
    # vs sequential: 5s + 5s + 5s = 15s
```

### Selective Execution:
```python
def test_selective(api_clients):
    # Only create what you need
    owner = api_clients.owner  # Created
    # member and member_2 NOT accessed = NOT created (saves resources)
    
    owner.api.collections.get()
```

## 🔧 Troubleshooting

### Issue: Need to pass additional parameters
**Solution**: Parameters are pre-configured in fixture. To customize, access the dict directly:
```python
# If you need custom params (bypass DotDict auto-execution)
raw_config = dict(api_clients.owner)
raw_config['device_uid'] = 'custom-device'
client = raw_config['function'](**{k: v for k, v in raw_config.items() if k != 'function'})
```

### Issue: Client created multiple times
**Solution**: DotDict caches the result. First access executes function, subsequent accesses return cached client:
```python
owner1 = api_clients.owner  # Executes setup_api_client()
owner2 = api_clients.owner  # Returns cached client (same instance)
assert owner1 is owner2  # True
```

### Issue: Want to force re-create client
**Solution**: Delete the key and access again:
```python
del api_clients['owner']
owner = api_clients.owner  # Re-executes setup_api_client()
```

## 🔄 Backward Compatibility

Legacy fixtures still work:

```python
# Old style - still supported
def test_mac_legacy(mac):
    mac.click_element('button')

def test_ios_legacy(ios):
    # Parameterized - runs twice (iPhone + iPad)
    ios.find_element('icon').click()

def test_iphone_legacy(iphone):
    iphone.launch_app()

def test_ipad_legacy(ipad):
    ipad.launch_app()
```

## ⚙️ Configuration Details

### How Parameters Work

Parameters in the fixture dict are **automatically passed** to the setup function:

```python
api_clients = DotDict(
    owner=dict(
        function=setup_api_client,      # ← This function will be called
        username='test@test.com',        # ← Passed as username=...
        password='pass123',              # ← Passed as password=...
        service_type=APIServiceType.API  # ← Passed as service_type=...
    )
)

# When accessed:
owner = api_clients.owner
# → Calls: setup_api_client(username='test@test.com', password='pass123', service_type=...)
# → Returns: APIClient instance
```

### Adding Custom Parameters

If your test needs custom parameters, you can still use the fixture flexibly:

```python
def test_custom(api_clients, proj_config):
    # Access raw config if needed
    owner_config = dict(api_clients.owner)
    
    # Call with custom params (bypasses DotDict auto-execution)
    owner = owner_config['function'](
        user=owner_config['username'],
        password=owner_config['password'],
        service_type=APIServiceType.ADMIN,  # ← Custom: use admin service
        device_uid='custom-device-123'       # ← Custom: specific device
    )
```

## 🔄 DotDict Behavior Details

### Execution Flow:

```python
# 1. Define fixture
api_clients = DotDict(
    owner=dict(function=setup_api_client, username='test', password='pass')
)

# 2. First access - executes function
owner1 = api_clients.owner
# → setup_api_client(username='test', password='pass') is called
# → Returns APIClient instance
# → Stores result: api_clients['owner'] = <APIClient>

# 3. Second access - returns cached result
owner2 = api_clients.owner
# → Returns cached APIClient instance (no function call)
# → owner1 is owner2 → True (same object!)

# 4. Access another attribute - independent execution
member = api_clients.member
# → setup_api_client(username='member1', password='pass') is called
# → New APIClient instance for member
```

### Thread Safety & Parallel Execution:

```python
def test_parallel_dotdict(api_clients):
    # These 3 accesses happen sequentially in THIS function
    # BUT the setup_api_client() calls run in parallel threads!
    owner = api_clients.owner      # ← Triggers thread 1 (returns Future internally)
    member = api_clients.member    # ← Triggers thread 2 (returns Future internally)
    member_2 = api_clients.member_2  # ← Triggers thread 3 (returns Future internally)
    
    # When you USE the clients, they block/wait if not ready
    owner.api.collections.get()    # ← Waits for thread 1 if needed
    member.api.collections.get()   # ← Waits for thread 2 if needed
```

## 📈 Performance Analysis

### Scenario 1: Sequential Access (Old Way - No DotDict)
```python
# Manual, sequential
owner = setup_api_client('user1', 'pass', wait=True)     # 5s
member = setup_api_client('user2', 'pass', wait=True)    # 5s
member_2 = setup_api_client('user3', 'pass', wait=True)  # 5s
# Total: 15s
```

### Scenario 2: DotDict Auto-Parallel (New Way!)
```python
# DotDict magic - automatic parallel!
owner = api_clients.owner      # Starts in thread (returns immediately)
member = api_clients.member    # Starts in thread (returns immediately)
member_2 = api_clients.member_2  # Starts in thread (returns immediately)
# All 3 threads running in parallel: max(5s, 5s, 5s) = 5s
# Total: ~5s (3x faster!)
```

### Scenario 3: Selective Loading (Most Efficient!)
```python
# Only create what you need
owner = api_clients.owner  # Created (5s)
# member NOT accessed = NOT created (0s saved)
# member_2 NOT accessed = NOT created (0s saved)
# Total: 5s (vs 15s if all created)
```

## 📚 Examples

See `examples/test_unified_clients.py` for comprehensive examples.

## 🔧 Troubleshooting

### Issue: Clients not starting in parallel
**Solution**: Make sure you're not using `wait=True` when you want parallel execution.

### Issue: Need to access client attributes
**Solution**: Access via the dict:
```python
username = api_clients.owner['username']
password = api_clients.owner['password']
```

### Issue: Want to add more clients
**Solution**: Extend the fixture:
```python
@pytest.fixture(scope="session")
def extended_api_clients(api_clients, proj_config):
    # Add member_3
    api_clients.member_3 = dict(
        function=setup_api_client,
        username=proj_config["member_prefix"] + "3" + proj_config["domain"],
        password=proj_config["password"],
        service_type=APIServiceType.API
    )
    return api_clients

# Usage
def test_extended(extended_api_clients):
    member_3 = extended_api_clients.member_3  # Auto-executes!
```

## 🎯 Summary

✅ **5 client types**: API, Web, Mac, iPhone, iPad  
✅ **3 instances each**: owner, member, member_2  
✅ **Total**: 15 clients can run in parallel  
✅ **Unified pattern**: Same structure for all types  
✅ **Auto-execution**: DotDict magic - just access attribute!  
✅ **Lazy loading**: Only creates clients you actually use  
✅ **Cached**: First access executes, subsequent accesses return same instance  
✅ **Parallel by default**: All setup functions run in threads automatically  
✅ **Backward compatible**: Legacy fixtures still work  
✅ **Performance**: 3-10x faster with parallel execution  
