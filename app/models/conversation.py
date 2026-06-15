from typing import List

from app.db.base import Base
from sqlalchemy import Integer, String, DateTime, Text
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    session_id: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(200), default='新对话')
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    messages: Mapped[List["Message"]] = relationship(
        primaryjoin=' Conversation.id == foreign(Message.conversation_id)',
        back_populates="conversation"
    )


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    conversation_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    conversation: Mapped["Conversation"] = relationship(
        primaryjoin='foreign(Message.conversation_id) == Conversation.id',
        back_populates="messages"

    )
