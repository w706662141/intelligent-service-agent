from typing import List, Dict


class ContextPruner:

    def __init__(self, max_turns: int = 6, max_chars: int = 4000):
        """
        max_turns: 最多保留最近 N 轮（user + assistant = 1 轮）
        max_chars: 字符级兜底（防止 prompt 过长）
        """

        self.max_turns = max_turns
        self.max_chars = max_chars

    def prune(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        裁剪入口
        """
        messages = self._prune_by_turns(messages)
        messages = self._prune_by_chars(messages)
        return messages

    def _prune_by_turns(self, messages: List[Dict[str, str]]):
        if self.max_turns <= 0:
            return messages
        max_msgs = self.max_turns * 2
        return messages[-max_msgs:]

    def _prune_by_chars(self, messages: List[Dict[str, str]]):
        total_chars = 0
        result = []

        for msg in reversed(messages):
            length = len(msg["content"])
            if total_chars + length > self.max_chars:
                break
            result.append(msg)
            total_chars += length

        return list(reversed(result))
