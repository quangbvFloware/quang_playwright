# framework/core/user_registry.py
import json
from pathlib import Path
from threading import Lock


class UserRegistry:
    """
    Registry để track users đã được verify/signup
    Thread-safe cho parallel execution
    """
    
    def __init__(self, cache_file=None):
        self.cache_file = cache_file or Path('.pytest_cache/user_registry.json')
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        
        self._users = {}  # {email: {'exists': True/False, 'verified': True}}
        self._lock = Lock()
        
        # Load cache từ file nếu có
        self._load_cache()
    
    def _load_cache(self):
        """Load cached user data"""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, 'r') as f:
                    self._users = json.load(f)
            except:
                self._users = {}
    
    def _save_cache(self):
        """Save user data to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self._users, f, indent=2)
    
    def is_verified(self, email):
        """Check xem user đã được verify chưa"""
        with self._lock:
            return email in self._users and self._users[email].get('verified', False)
    
    def mark_exists(self, email, exists=True):
        """Đánh dấu user tồn tại"""
        with self._lock:
            if email not in self._users:
                self._users[email] = {}
            self._users[email]['exists'] = exists
            self._users[email]['verified'] = True
            self._save_cache()
    
    def mark_signed_up(self, email, unused=False):
        """Đánh dấu user đã được signup"""
        with self._lock:
            if email not in self._users:
                self._users[email] = {}
            self._users[email]['exists'] = True
            self._users[email]['verified'] = True
            self._users[email]['signed_up_by_test'] = True
            self._users[email]['unused'] = unused
            self._save_cache()
    
    def get_user_info(self, email):
        """Lấy thông tin user"""
        with self._lock:
            return self._users.get(email, {})
    
    def clear(self):
        """Clear registry (dùng cho cleanup)"""
        with self._lock:
            self._users = {}
            self._save_cache()