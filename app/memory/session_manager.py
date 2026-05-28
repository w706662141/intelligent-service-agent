import hashlib
import time
import threading
from dataclasses import dataclass, field
from typing import List

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

    def __init__(self, expire_seconds: int = 1800, shard_size: int = 16):
        self._expire_seconds = expire_seconds
        self._shard_size = shard_size

        # 初始化 16 个独立的桶（分片），每个分片有自己专属的字典和锁
        self._shards = [
            {'sessions': {}, 'lock': threading.Lock()}
            for _ in range(self._shard_size)
        ]

    def _get_shard(self, key: str) -> dict:
        """通过哈希算法，决定这个 key 归哪把锁/分片管"""
        hasher = hashlib.md5(key.encode('utf-8'))

        shard_index = int(hasher.hexdigest(), 16) % self._shard_size

        return self._shards[shard_index]

    def get_or_create(self, user_id: str, session_id: str, role: str = "user") -> Session:
        key = f"{user_id}:{session_id}"
        shard = self._get_shard(key)

        if key in shard['sessions']:
            session = shard['sessions'][key]
            session.touch()
            return session

        new_session = Session(user_id=user_id, role=role)
        new_session.touch()

        with shard['lock']:
            if key not in shard['sessions']:
                shard['sessions'][key] = new_session
            else:
                new_session = shard['sessions'][key]
                new_session.touch()
            return new_session

    def remove(self, user_id: str, session_id: str) -> bool:
        key = f"{user_id}:{session_id}"
        shard = self._get_shard(key)
        removed_session = None

        with shard['lock']:
            if key in shard['sessions']:
                removed_session = shard['sessions'].pop(key)

        if removed_session:
            try:
                removed_session.memory.clear()
            except Exception:
                pass
            return True
        return False

    def remove_user(self, user_id: str) -> int:
        """删除该用户的所有会话"""
        prefix = f"{user_id}:"
        removed_sessions: List[Session] = []

        # 轮流锁住每一个分片，捞出属于该用户的所有 session
        for shard in self._shards:
            with shard['lock']:
                keys_to_remove = [
                    k for k in shard['sessions'] if k.startswith(prefix)]

                for key in keys_to_remove:
                    removed_sessions.append(shard['sessions'].pop(key))
        for session in removed_sessions:
            try:
                session.memory.clear()
            except Exception:
                pass

        return len(removed_sessions)

    def cleanup_expired(self) -> int:
        now = time.time()
        expired_sessions: List[Session] = []

        for shard in self._shards:
            with shard['lock']:
                expired_keys = [
                    uid for uid, s in shard['sessions'].items()
                    if now - s.last_active > self._expire_seconds
                ]
                for uid in expired_keys:
                    expired_sessions.append(shard['sessions'].pop(uid))

        for session in expired_sessions:
            try:
                session.memory.clear()
            except Exception:
                pass

        return len(expired_sessions)

    @property
    def active_count(self) -> int:
        """统计所有分片的活跃会话总数（无锁读取提高吞吐量）"""
        # 注意：这里没有加锁，在极端写入并发下可能存在微小的数量滞后，但换来了超高读取性能，完全符合监控或统计场景
        return sum(len(shard['sessions']) for shard in self._shards)
