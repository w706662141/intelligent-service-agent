from datetime import datetime
from typing import List, Dict

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Message, Conversation
from app.memory.redis_memory import RedisMemory


class MemoryManager:

    def __init__(self,
                 db: AsyncSession,
                 redis_memory: RedisMemory
                 ):
        self.db = db
        self.redis = redis_memory

    # 保存用户消息
    async def save_user_message(self,
                                conversation_id: int,
                                content: str
                                ):
        message = Message(
            conversation_id=conversation_id,
            role='user',
            content=content
        )

        self.db.add(message)

        await self.redis.add_message(
            conversation_id,
            'user',
            content
        )

    # 保存AI消息

    async def save_ai_message(self,
                              conversation_id: int,
                              content: str
                              ):
        message = Message(
            conversation_id=conversation_id,
            role='assistant',
            content=content
        )

        self.db.add(message)

        await self.redis.add_message(
            conversation_id,
            'assistant',
            content
        )

    async def commit(self):
        await self.db.commit()

    async def get_context(
            self,
            conversation_id: int
    ):
        history = await self.redis.get_messages(
            conversation_id=conversation_id
        )

        if history:
            return history

        return await self.restore_from_mysql(
            conversation_id
        )

    async def restore_from_mysql(
            self,
            conversation_id: int):
        stmt = (
            select(Message)
                .where(
                Message.conversation_id
                == conversation_id
            )
                .order_by(
                Message.created_at.desc()
            )
                .limit(20)
        )

        result = await self.db.execute(stmt)

        messages = result.scalars().all()

        messages.reverse()

        history = []

        for msg in messages:
            history.append(
                {
                    'role': msg.role,
                    'content': msg.content
                }
            )

            await self.redis.add_message(
                conversation_id,
                msg.role,
                msg.content,
            )

        return history


    async def _update_conversation_title(
            self,
            conversation_id: int,
            title: str,
            is_first_message: bool = False):
        """根据第一条消息更新会话标题"""
        if is_first_message:
            title_length = len(title)

            title = title.strip()[:30]
            if title_length > 30:
                title += "..."

        stmt = update(Conversation).where(
            Conversation.id == conversation_id) \
            .values(title=title,
                    updated_at=datetime.utcnow())

        await self.db.execute(stmt)
        await self.db.commit()

    async def auto_update_title_from_first_message(
            self,
            conversation_id: int,
            first_message: str):

        await self._update_conversation_title(
            conversation_id,
            first_message,
            is_first_message=True)
