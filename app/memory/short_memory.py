from collections import deque
from typing import Dict, List


class ShortTermMemory:
    """
    短期对话记忆（滑动窗口）
    """

    def __init__(self):
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        self.messages.append({
            'role': role,
            "content": content
        })

    def get(self) -> List[Dict[str, str]]:
        return self.messages

    def clear(self):
        self.messages.clear()
