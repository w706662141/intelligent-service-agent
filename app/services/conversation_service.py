from datetime import datetime
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.memory.redis_memory import RedisMemory
from app.models.conversation import Conversation
from app.services.message_service import MessageService


class ConversationService:

    def __init__(self, db: AsyncSession,
                 redis_memory: RedisMemory):
        self.db = db
        self.redis_memory = redis_memory
        self.message_service = MessageService(db)

    async def create_conversation(
            self,
            user_id: int):
        conversation = Conversation(
            user_id=user_id,
            session_id=str(uuid4()),
            title="新对话",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self.db.add(conversation)

        await self.db.commit()

        await self.db.refresh(conversation)

        return conversation

    async def get_list_conversation(
            self,
            user_id):
        stmt = select(Conversation) \
            .where(Conversation.user_id == user_id) \
            .order_by(Conversation.updated_at.desc())
        result = await self.db.execute(stmt)

        return result.scalars().all()

    async def get_conversation(
            self,
            conversation_id: int):
        stmt = select(Conversation) \
            .where(Conversation.id == conversation_id
                   )
        result = await self.db.execute(stmt)

        return result.scalar_one_or_none()

    async def update_title(
            self,
            conversation_id: int,
            title: str):
        stmt = update(Conversation) \
            .where(Conversation.id == conversation_id) \
            .values(
            title=title,
            updated_at=datetime.utcnow())

        await self.db.execute(stmt)
        await self.db.commit()

    async def delete_conversation(
            self,
            conversation_id: int):
        """
        删除整个会话

        删除：
        1. Message
        2. Conversation
        3. Redis缓存
        """
        conversation = await self.get_conversation(conversation_id)
        if not conversation:
            return False

        await self.message_service.delete_messages(conversation_id)

        stmt = delete(Conversation).where(
            Conversation.id == conversation_id
        )

        await self.db.execute(stmt)

        await self.db.commit()

        await self.redis_memory.delete_conversation(conversation_id)

        return True
