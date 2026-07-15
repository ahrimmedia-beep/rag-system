import threading
from collections import defaultdict

from app.domain.models import Message


class MemoryService:
    def __init__(self, window: int = 20) -> None:
        self._window = window
        self._store: dict[str, list[Message]] = defaultdict(list)
        self._lock = threading.Lock()

    def get(self, session_id: str) -> list[Message]:
        with self._lock:
            return list(self._store[session_id])

    def append(self, session_id: str, user: str, assistant: str) -> None:
        with self._lock:
            history = self._store[session_id]
            history.append(Message(role="user", content=user))
            history.append(Message(role="assistant", content=assistant))
            if len(history) > self._window:
                self._store[session_id] = history[-self._window :]
