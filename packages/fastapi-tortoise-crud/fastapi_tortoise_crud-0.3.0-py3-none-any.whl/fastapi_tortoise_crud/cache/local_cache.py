from typing import Optional, Any, Dict
from collections import OrderedDict
import time
import threading

class LocalCache:
    def __init__(self, max_size: int = 1000, ttl: int = 300):
        self.max_size = max_size
        self.default_ttl = ttl
        self.cache: OrderedDict = OrderedDict()
        self.expires: Dict[str, float] = {}
        self._lock = threading.Lock()
        
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self.cache:
                return None
                
            # 检查是否过期
            if self._is_expired(key):
                self._remove(key)
                return None
                
            # 更新访问顺序
            value = self.cache.pop(key)
            self.cache[key] = value
            return value
            
    def put(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        with self._lock:
            if key in self.cache:
                self._remove(key)
                
            # 如果缓存已满,删除最早的项
            while len(self.cache) >= self.max_size:
                self.cache.popitem(last=False)
                
            self.cache[key] = value
            self.expires[key] = time.time() + (ttl or self.default_ttl)
            
    def delete(self, key: str) -> None:
        with self._lock:
            self._remove(key)
            
    def clear(self) -> None:
        with self._lock:
            self.cache.clear()
            self.expires.clear()
            
    def _is_expired(self, key: str) -> bool:
        return time.time() > self.expires.get(key, 0)
        
    def _remove(self, key: str) -> None:
        self.cache.pop(key, None)
        self.expires.pop(key, None)
        
    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "keys": list(self.cache.keys())
            } 