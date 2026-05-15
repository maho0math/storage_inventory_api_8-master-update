import json
import redis
from typing import Any, Optional
from app.core.config import settings

class CacheService:
    def __init__(self):
        self._client = redis.from_url(
            settings.REDIS_URL, 
            decode_responses=True 
        )
        self.prefix = "storage:"

    def _get_full_key(self, key: str) -> str:
        
        return f"{self.prefix}{key}"

    def set(self, key: str, value: Any, ttl: int = settings.CACHE_TTL_DEFAULT) -> None:
 
        full_key = self._get_full_key(key)
        serialized_value = json.dumps(value)
        self._client.set(full_key, serialized_value, ex=ttl)

    def get(self, key: str) -> Optional[Any]:

        full_key = self._get_full_key(key)
        data = self._client.get(full_key)
        if data:
            return json.loads(data)
        return None

    def delete(self, key: str) -> None:

        full_key = self._get_full_key(key)
        self._client.delete(full_key)

    def delete_by_pattern(self, pattern: str) -> None:

        full_pattern = self._get_full_key(pattern)
        keys = self._client.keys(full_pattern)
        if keys:
            self._client.delete(*keys)

cache_service = CacheService()