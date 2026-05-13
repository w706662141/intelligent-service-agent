
from typing import Dict, List


class ShortTermMemory:
    """
    短期对话记忆（滑动窗口）
    """

    def __init__(self, max_turns: int = 20):
        self.messages: List[Dict[str, str]] = []
        self.max_turns = max_turns

    def add(self, role: str, content: str):
        self.messages.append({
            'role': role,
            "content": content
        })
        if len(self.messages) > self.max_turns:
            self.messages = self.messages[-self.max_turns:]

    def get(self) -> List[Dict[str, str]]:
        return self.messages

    def clear(self):
        self.messages.clear()
