from typing import List

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Message


class MessageService:
    def __init__(self,
                 db: AsyncSession):
        self.db = db

    async def save_message(
            self,
            conversation_id: int,
            role: str,
            content: str) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )

        self.db.add(message)
        return message

    async def get_messages(
            self,
            conversation_id: int,
            page: int = 1,
            size: int = 50) -> List[dict]:
        offset = (page - 1) * size
        stmt = select(Message) \
            .where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.asc()).offset(offset) \
            .limit(size)

        result = await self.db.execute(stmt)

        messages = result.scalars().all()

        return [
            {
                'id': msg.id,
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            } for msg in messages
        ]

    async def get_recent_messages(
            self,
            conversation_id: int,
            limit: int = 20):
        stmt = select(Message) \
            .where(Message.conversation_id == conversation_id) \
            .order_by(Message.created_at.desc()) \
            .limit(limit)

        result = await self.db.execute(stmt)

        messages = result.scalars().all()

        messages.reverse()

        return messages

    async def delete_messages(
            self,
            conversation_id: int):
        stmt = delete(Message) \
            .where(Message.conversation_id == conversation_id
                   )

        await self.db.execute(stmt)

    async def count_messages(
            self,
            conversation_id: int
    ):
        stmt = select(Message) \
            .where(Message.conversation_id == conversation_id)

        result = await self.db.execute(stmt)

        return len(result.scalars().all())
