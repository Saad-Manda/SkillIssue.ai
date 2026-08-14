import json
import redis
from typing import Any, Dict
from .turn import Turn
from ...config import settings



def parse_chat_history(raw: list) -> list[Turn]:
    return [Turn(**t) if isinstance(t, dict) else t for t in raw]


class RedisSessionStore:
    def __init__(self, url=settings.REDIS_URL):
        self.client = redis.from_url(url, decode_responses=True)

    def _key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def get(self, session_id: str) -> Dict[str, Any]:
        raw = self.client.get(self._key(session_id))
        if raw is None:
            return {"chat_history": [], "phasewise_summary": []}
        return json.loads(raw)

    def set(self, session_id: str, data: Dict[str, Any], ttl: int | None = None):
        key = self._key(session_id)
        payload = json.dumps(data)
        if ttl:
            self.client.setex(key, ttl, payload)
        else:
            self.client.set(key, payload)

    def update(self, session_id: str, data: Dict[str, Any] | None = None, **kwargs):
        """
        Update the stored session state.

        Supports two calling styles:
        - update(session_id, {"faah": "bar"})
        - update(session_id, faah="bar")
        or a combination of both.
        """
        state = self.get(session_id)
        if data is not None:
            if isinstance(data, dict):
                state.update(data)
            else:
                raise TypeError("data must be a dict if provided")
        if kwargs:
            state.update(kwargs)
        self.set(session_id, state)


session_store = RedisSessionStore()
