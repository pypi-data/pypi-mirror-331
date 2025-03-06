"""
Cache implementation for Rust documentation
"""

import time
from dataclasses import dataclass
from typing import Dict, Optional
from rich.console import Console

console = Console(stderr=True)

@dataclass
class CachedDoc:
    """Cached documentation entry"""
    content: str
    timestamp: float
    byte_size: int


class DocumentationCache:
    """Cache for documentation to improve performance"""
    
    def __init__(self, expiry_seconds: int = 300):  # 5 minutes default
        self.cache: Dict[str, CachedDoc] = {}
        self.expiry_seconds = expiry_seconds
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[str]:
        """Get cached documentation if available and not expired"""
        if key in self.cache:
            doc = self.cache[key]
            if time.time() - doc.timestamp < self.expiry_seconds:
                self.hits += 1
                console.log(f"Cache hit for {key} ({doc.byte_size} bytes)")
                return doc.content
            else:
                # Expired entry
                console.log(f"Cache entry expired for {key}")
                del self.cache[key]
        
        self.misses += 1
        return None
    
    def set(self, key: str, content: str) -> None:
        """Cache documentation with current timestamp"""
        self.cache[key] = CachedDoc(
            content=content,
            timestamp=time.time(),
            byte_size=len(content.encode('utf-8'))
        )
        console.log(f"Cache miss for {key} ({len(content.encode('utf-8'))} bytes)")
    
    def clear(self) -> None:
        """Clear all cached entries"""
        count = len(self.cache)
        self.cache.clear()
        console.log(f"Cleared {count} cache entries")
    
    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "entries": len(self.cache),
            "hits": self.hits, 
            "misses": self.misses,
            "hit_ratio": round(self.hits / max(1, (self.hits + self.misses)) * 100, 1)
        }