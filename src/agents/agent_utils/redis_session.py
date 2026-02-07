import json
from typing import Any, Dict

import redis

from ...config import settings


class RedisSessionStore:
    def __init__(self, url=settings.REDIS_URL):
        self.client = redis.from_url(url, decode_responses=True)

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def get(self, session_id: str) -> Dict[str, Any]:
        raw = self.client.get(self._key(session_id))
        if raw is None:
            return {"user": None, "user_summary": None, "chat_history": []}
        return json.loads(raw)

    def set(self, session_id: str, data: Dict[str, Any], ttl: int | None = None):
        key = self._key(session_id)
        payload = json.dumps(data)
        if ttl:
            self.client.setex(key, ttl, payload)
        else:
            self.client.set(key, payload)

    def update(self, session_id: str, **kwargs):
        state = self.get(session_id)
        state.update(kwargs)
        self.set(session_id, state)


session_store = RedisSessionStore()
