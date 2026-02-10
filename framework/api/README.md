# API Framework - APIClient & URLBuilder

## Overview

This framework provides two main tools for working with APIs:

1. **APIClient** - Full-featured HTTP client with automatic endpoint loading
2. **URLBuilder** - Lightweight URL builder without instance creation overhead

Both tools share the same endpoint cache for optimal performance.

---

## URLBuilder

### Why URLBuilder?

Use `URLBuilder` when you only need to build URLs without making HTTP requests. It's more lightweight than creating an `APIClient` instance.

**Benefits:**
- ✅ No `APIClient` instance creation needed
- ✅ No `requests.Session` overhead
- ✅ Shares cache with `APIClient` (endpoint.yaml loaded only once)
- ✅ Thread-safe
- ✅ Simple and clean API

### Basic Usage

```python
from framework.api import URLBuilder

# Build full URLs
url = URLBuilder.build('oauth2', 'signup')
# → "https://oauth2-api.k8s.flostage.com/signup"

url = URLBuilder.build('admin', 'users_2fa_enable')
# → "https://admin-api.k8s.flostage.com/users/2fa/enable"

url = URLBuilder.build('api', 'chat_messages')
# → "https://v41-api.k8s.flostage.com/chat/messages"
```

### Shortcut Function

```python
from framework.api import build_url

url = build_url('oauth2', 'token')
# Same as URLBuilder.build('oauth2', 'token')
```

### Get URL Parts Separately

```python
# Get base URL only
base_url = URLBuilder.service_url('admin')
# → "https://admin-api.k8s.flostage.com"

# Get endpoint path only
path = URLBuilder.endpoint_path('admin', 'users_2fa_enable')
# → "/users/2fa/enable"
```

### List Available Services and Endpoints

```python
# List all services
services = URLBuilder.list_services()
# → ['api', 'oauth2', 'admin', 'chime', 'web', ...]

# List endpoints for a service
endpoints = URLBuilder.list_endpoints('oauth2')
# → ['signup', 'token', 'checkemail', 'refresh', ...]

endpoints = URLBuilder.list_endpoints('api')
# → ['chat_messages', 'collections', 'clouds', ...]
```

### Cache Management

```python
# Get cache information
info = URLBuilder.cache_info()
print(info)
# {
#     'loaded': True,
#     'services': 10,
#     'total_endpoints': 150,
#     'endpoints_per_service': {'api': 100, 'oauth2': 10, ...}
# }

# Clear cache (useful for testing)
URLBuilder.clear_cache()
```

---

## APIClient

### Basic Usage

```python
from framework.api import APIClient

# Create client
client = APIClient(headers={'Authorization': 'Bearer token'})

# Make requests using service.endpoint syntax
response = client.oauth2.signup.post(json={
    'email': 'user@example.com',
    'password': 'pass123'
})

response = client.api.chat_messages.get(params={'channel_id': '123'})

response = client.admin.users_2fa_enable.put()
```

### Get URL from APIClient

```python
client = APIClient()

# Get URL from endpoint
url = client.oauth2.signup.url
# → "https://oauth2-api.k8s.flostage.com/signup"

# Make request
response = client.oauth2.signup.post(json={...})
```

### Direct Path (Flexible)

```python
# Can still use direct paths if endpoint not in yaml
response = client.api.get('/custom/endpoint', params={...})
response = client.oauth2.post('/custom-signup', json={...})
```

---

## Shared Cache Performance

Both `URLBuilder` and `APIClient` share the same endpoint cache:

```python
from framework.api import URLBuilder, APIClient

# Scenario 1: URLBuilder first
url = URLBuilder.build('oauth2', 'signup')  # Loads endpoint.yaml
client = APIClient()
response = client.oauth2.token.post(...)     # Uses cached endpoints ✓

# Scenario 2: APIClient first
client = APIClient()
response = client.api.collections.get()      # Loads endpoint.yaml
url = URLBuilder.build('oauth2', 'signup')   # Uses cached endpoints ✓

# Result: endpoint.yaml is only loaded ONCE regardless of order
```

---

## Use Cases

### Use URLBuilder when:

- ✅ You only need URL strings (for logging, external tools, etc.)
- ✅ You're not making HTTP requests
- ✅ You want minimal overhead
- ✅ Building URLs in helper functions

**Example: auth_helper.py**
```python
from framework.api import URLBuilder

def get_token(user, password):
    resp = requests.post(
        url=URLBuilder.build('oauth2', 'token'),  # ← No APIClient needed!
        headers=headers,
        json={'username': user, 'password': password}
    )
    return resp.json()
```

### Use APIClient when:

- ✅ Making HTTP requests
- ✅ Need request session management
- ✅ Want built-in request methods (get, post, put, delete)
- ✅ Need connection pooling

**Example:**
```python
from framework.api import APIClient

client = APIClient(headers={'Authorization': 'Bearer token'})

# Make requests directly
response = client.api.collections.get()
response = client.oauth2.token.post(json={...})
```

---

## Configuration

Endpoints are defined in `resources/yaml/endpoint.yaml`:

```yaml
oauth2:
  signup: /signup
  token: /token
  checkemail: /checkemail
  
api:
  chat_messages: /chat/messages
  collections: /collections
  
admin:
  users_2fa_enable: /users/2fa/enable
```

Service base URLs are defined in config files (`config/staging.yaml`, etc.):

```yaml
api: "https://v41-api.k8s.flostage.com"
oauth2: "https://oauth2-api.k8s.flostage.com"
admin: "https://admin-api.k8s.flostage.com"
```

---

## Examples

See `examples/test_url_builder.py` for comprehensive examples:

```bash
python examples/test_url_builder.py
```

---

## Error Handling

```python
from framework.api import URLBuilder

try:
    url = URLBuilder.build('nonexistent', 'endpoint')
except ValueError as e:
    print(e)
    # Service 'nonexistent' not found in config.
    # Available services: ['api', 'oauth2', 'admin', ...]

try:
    url = URLBuilder.build('oauth2', 'invalid_endpoint')
except ValueError as e:
    print(e)
    # Endpoint 'invalid_endpoint' not found for service 'oauth2'.
    # Available endpoints: ['signup', 'token', 'checkemail', ...]
```

---

## Performance Notes

- **Endpoint loading:** Only happens once per Python process
- **Thread-safe:** Safe for parallel execution
- **Memory efficient:** Shared cache across all instances
- **Zero overhead:** URLBuilder has no session/connection overhead

---

## Migration Guide

### Before (using APIClient just for URLs):

```python
_api_client = APIClient()
url = _api_client.admin.users_2fa_enable.url
```

### After (using URLBuilder):

```python
url = URLBuilder.build('admin', 'users_2fa_enable')
```

**Benefits:**
- No APIClient instance creation
- No Session object
- Same result, less overhead
