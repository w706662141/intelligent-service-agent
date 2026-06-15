from typing import Dict, Optional, List

from app.agent.executor import ReActPlanExecutor, ExecutionContext
from app.models.conversation import Conversation, Message
from app.memory.memory_manager import MemoryManager
from app.memory.redis_memory import RedisMemory

from datetime import datetime
from sqlalchemy import select


class PersistentSession:

    def __init__(self,
                 conversation_id: int,
                 user_id: str,
                 session_id: str,
                 role: str,
                 memory_manager: MemoryManager,
                 executor: ReActPlanExecutor):

        self.conversation_id = conversation_id
        self.user_id = user_id
        self.session_id = session_id
        self.role = role
        self.memory_manager = memory_manager
        self.executor = executor
        self._history = Optional[List[Dict]] = None

    async def run(self, question: str):
        if self._history is None:
            self._history = await self.memory_manager.get_context(self.conversation_id)

        context = ExecutionContext(
            session_id=str(self.conversation_id),
            role='assistant',
            history=self._history
        )

        # context = await self.memory_manager.get_context(
        #     self.conversation_id
        # )

        full_response = ''

        async for chunk in self.executor.run(question, context):
            full_response += chunk
            yield chunk

        await self.memory_manager.save_user_message(
            self.conversation_id,
            question
        )
        await self.memory_manager.save_ai_message(
            self.conversation_id,
            full_response
        )
        self._history.append({"role": "user", "content": question})
        self._history.append({"role": "assistant", "content": full_response})

        await self.memory_manager.commit()

        if len(context.history) == 0:
            await self.memory_manager. \
                auto_update_title_from_first_message(
                self.conversation_id,
                question)

    async def delete(self):
        await self.memory_manager.delete_conversations(self.conversation_id)


class PersistentSessionManager:

    def __init__(self,
                 db_session_factory,
                 redis_client,
                 executor_class
                 ):
        self.db_session_factory = db_session_factory
        self.redis_memory = RedisMemory(redis_client)
        self.executor_class = executor_class
        self._sessions: Dict[str, PersistentSession] = {}

    async def get_or_create(self,
                            user_id: str,
                            session_id: str,
                            role: str,
                            ) -> PersistentSession:
        cache_key = f"{user_id}:{session_id}"

        if cache_key in self._sessions:
            return self._sessions[cache_key]

        async with self.db_session_factory() as db:
            stmt = select(Conversation).where(
                Conversation.user_id == int(user_id),
                Conversation.session_id == session_id
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()

            if not conversation:
                conversation = Conversation(
                    user_id=int(user_id),
                    session_id=session_id,
                    title='新对话',
                    create_at=datetime.utcnow(),
                    update_at=datetime.utcnow()
                )
                db.add(conversation)
                await db.commit()
                await db.refresh(conversation)

            memory_manager = MemoryManager(db, self.redis_memory)

            executor = self.executor_class(role=role)

            session = PersistentSession(
                conversation_id=conversation.id,
                user_id=user_id,
                session_id=session_id,
                role=role,
                memory_manager=memory_manager,
                executor=executor
            )

            self._sessions[cache_key] = session

            return session

    async def delete_session(
            self,
            user_id: str,
            session_id: str):

        cache_key = f"{user_id}:{session_id}"

        session = self._sessions.get(cache_key)

        if session:
            result = await session.delete()
            del self._sessions[cache_key]
            return result

        async with self.db_session_factory() as db:
            stmt = select(Conversation).where(
                Conversation.user_id == int(user_id),
                Conversation.session_id == session_id,
            )
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()

            if conversation:
                memory_manager = MemoryManager(db, self.redis_memory)
                return await memory_manager.delete_conversations(conversation.id)

        return "删除失败"
