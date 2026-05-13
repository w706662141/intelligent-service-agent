import time
import threading
from dataclasses import dataclass, field
from typing import Dict

from app.memory.short_memory import ShortTermMemory
from app.memory.context_pruner import ContextPruner
from app.agent.executor import ReActPlanExecutor


@dataclass
class Session:
    user_id: str
    role: str
    memory: ShortTermMemory = field(default_factory=ShortTermMemory)
    pruner: ContextPruner = field(default_factory=lambda: ContextPruner(max_turns=5, max_chars=3000))
    executor: ReActPlanExecutor = field(init=False)
    last_active: float = field(default_factory=time.time)

    def __post_init__(self):
        self.executor = ReActPlanExecutor(role=self.role)

    def touch(self):
        self.last_active = time.time()


class SessionManager:
    """管理所有用户会话，线程安全，支持自动过期 + 手动清除"""

    def __init__(self, expire_seconds: int = 1800):
        self._sessions: Dict[str, Session] = {}
        self._lock = threading.Lock()
        self._expire_seconds = expire_seconds

    def get_or_create(self, user_id: str, session_id: str, role: str = "user") -> Session:
        key = f"{user_id}:{session_id}"
        with self._lock:
            session = self._sessions.get(key)
            if session is None:
                session = Session(user_id=user_id, role=role)
                self._sessions[key] = session
            session.touch()
            return session

    def remove(self, user_id: str, session_id: str) -> bool:
        key = f"{user_id}:{session_id}"
        with self._lock:
            session = self._sessions.pop(key, None)
            if session:
                session.memory.clear()
            return session is not None

    def remove_user(self, user_id: str) -> int:
        """删除该用户的所有会话"""
        with self._lock:
            keys = [k for k in self._sessions if k.startswith(f"{user_id}:")]
            for k in keys:
                self._sessions.pop(k).memory.clear()
            return len(keys)

    def cleanup_expired(self) -> int:
        now = time.time()
        with self._lock:
            expired = [
                uid for uid, s in self._sessions.items()
                if now - s.last_active > self._expire_seconds
            ]
            for uid in expired:
                self._sessions.pop(uid).memory.clear()
        return len(expired)

    @property
    def active_count(self) -> int:
        return len(self._sessions)
