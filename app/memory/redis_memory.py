import json
from redis.asyncio import Redis


class RedisMemory:
    def __init__(self,
                 redis_client: Redis,
                 max_messages: int = 20
                 ):
        self.redis = redis_client
        self.max_messages = max_messages

    def _key(self,
             conversation_id: int,
             ) -> str:
        return f"chat:{conversation_id}"

    async def add_message(self,
                          conversation_id: int,
                          role: str,
                          content: str
                          ):
        await self.redis.rpush(
            self._key(conversation_id),
            json.dumps(
                {
                    'role': role,
                    'content': content
                }
            )
        )

        await self.redis.ltrim(
            self._key(conversation_id),
            -self.max_messages,
            -1
        )

    async def get_messages(self,
                           conversation_id: int):
        items = await self.redis.lrange(
            self._key(conversation_id),
            0,
            -1
        )

        return [
            json.loads(item)
            for item in items
        ]

    async def delete_conversation(self,
                                  conversation_id: int):
        await self.redis.delete(
            self._key(conversation_id))