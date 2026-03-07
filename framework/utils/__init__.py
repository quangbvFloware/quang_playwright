from framework.utils.logging_util import logger


class DotDict(dict):
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value

    def _call_func(self, key, val):
        new_val = val
        func_key = "function"
        if isinstance(val, dict) and val.get(func_key) and callable(val.get(func_key)):
            try:
                func = val.get(func_key)
                kwargs = {k: val[k] for k in val if k != func_key}
                new_val = func(**kwargs)
                
                # If the function returns a Future, wait for result
                from concurrent.futures import Future
                if isinstance(new_val, Future):
                    new_val = new_val.result()
                    
            except Exception as e:
                # If function fails, fallback to original dict
                # This allows DotDict to convert it for attribute access
                logger.error(f"❌ DotDict error for key '{key}': {type(e).__name__}: {e}")
                new_val = val
            self[key] = new_val
        return new_val

    def __getitem__(self, key):
        res = super().__getitem__(key)
        res = self._call_func(key, res)

        if isinstance(res, dict):
            self[key] = DotDict(res)
        elif isinstance(res, list):
            for i in range(len(res)):
                if isinstance(res[i], dict):
                    res[i] = DotDict(res[i])
        return super().__getitem__(key)  # reload value again to get dotdict effect

    def __missing__(self, key):
        return rf"[~~missing-key-{key}~~]"

    def get(self, *args, **kwargs):
        res = super().get(*args, **kwargs)
        key = args[0] if args else kwargs.get("key")
        self._call_func(key, res)

        return super().get(*args, **kwargs)

    def values(self, is_raw=False):
        if is_raw:
            return super().values()
        _ = [self._call_func(key, val) for key, val in super().items()]
        return super().values()

    def items(self, is_raw=False):
        if is_raw:
            return super().items()
        _ = [self._call_func(key, val) for key, val in super().items()]
        return super().items()


# ========================================
# Helper Functions for Parallel Access
# ========================================

def parallel_get(*dot_dicts_with_keys):
    """
    Get multiple clients from DotDict fixtures in truly parallel execution
    
    This bypasses DotDict's auto-execution and sequential .result() calls
    to start all clients simultaneously, then waits for all to complete.
    
    Args:
        *dot_dicts_with_keys: Tuples of (dotdict, key) to access
    
    Returns:
        Tuple of clients in same order as input
    
    Example:
        >>> # Start API and Web clients in parallel
        >>> owner_api, owner_web = parallel_get(
        >>>     (api_clients, 'owner'),
        >>>     (web_clients, 'owner')
        >>> )
        >>> # Both start simultaneously, wait together at the end
        >>> 
        >>> # Or with different roles
        >>> owner_api, member_web, member_2_api = parallel_get(
        >>>     (api_clients, 'owner'),
        >>>     (web_clients, 'member'),
        >>>     (api_clients, 'member_2')
        >>> )
    """
    from concurrent.futures import Future
    
    tasks = []
    
    # Phase 1: Start all tasks WITHOUT blocking
    for dotdict, key in dot_dicts_with_keys:
        # Check if already cached (already a client, not dict)
        try:
            existing = dict.__getitem__(dotdict, key)
            if not isinstance(existing, dict) or 'function' not in existing:
                # Already a client - just return it
                tasks.append(('cached', existing, dotdict, key))
                continue
        except KeyError:
            pass
        
        # Get config
        config = dict.__getitem__(dotdict, key)
        func = config['function']
        kwargs = {k: v for k, v in config.items() if k != 'function'}
        
        # Call function - it returns Future immediately (runs in background thread)
        result = func(**kwargs)
        tasks.append(('future', result, dotdict, key))
    
    # Phase 2: Wait for ALL futures to complete (parallel wait!)
    results = []
    for task in tasks:
        if task[0] == 'cached':
            _, client, dotdict, key = task
            results.append(client)
        else:  # future
            _, future_or_client, dotdict, key = task
            
            # Check if it's actually a Future
            if isinstance(future_or_client, Future):
                # Wait for Future to complete
                client = future_or_client.result()
            else:
                # Already a client (shouldn't happen with setup functions)
                client = future_or_client
            
            # Cache back to DotDict so subsequent access is fast
            dotdict[key] = client
            results.append(client)
    
    return tuple(results)


def parallel_get_all(dotdict, *keys):
    """
    Get multiple keys from same DotDict in parallel
    
    Args:
        dotdict: DotDict fixture (e.g., api_clients)
        *keys: Keys to access (e.g., 'owner', 'member', 'member_2')
    
    Returns:
        Tuple of clients in same order as keys
    
    Example:
        >>> # Start all 3 API clients in parallel
        >>> owner, member, member_2 = parallel_get_all(
        >>>     api_clients, 'owner', 'member', 'member_2'
        >>> )
        >>> # All 3 start simultaneously!
        >>> 
        >>> # Or just 2 web clients
        >>> owner, member = parallel_get_all(web_clients, 'owner', 'member')
    """
    return parallel_get(*[(dotdict, key) for key in keys])