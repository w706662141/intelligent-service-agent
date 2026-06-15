from app.memory.memory_manager import MemoryManager
from app.services.message_service import MessageService
from app.agent.executor import (
    ReActPlanExecutor,
    ExecutionContext
)
from sqlalchemy.ext.asyncio import AsyncSession
from app.memory.redis_memory import RedisMemory
from app.redis.deps import get_redis_client


class ChatService:
    def __init__(
            self,
            memory_manager: MemoryManager,
            message_service: MessageService,
            executor: ReActPlanExecutor):
        self.memory_manager = memory_manager
        self.message_service = message_service
        self.executor = executor

    async def chat(
            self,
            conversation_id: int,
            question: str):
        """
        1. 获取上下文
        2. 执行Agent
        3. 保存消息
        """

        history = await self.memory_manager.get_context(conversation_id)

        context = ExecutionContext(
            session_id=str(conversation_id),
            role='assistant',
            history=history
        )

        full_response = ""

        async for chunk in self.executor.run(
                question,
                context
        ):
            full_response += chunk
            yield chunk

        # 保存用户消息
        await self.message_service.save_message(
            conversation_id=conversation_id,
            role='user',
            content=question
        )
        # 保存AI消息
        await self.message_service.save_message(
            conversation_id=conversation_id,
            role='assistant',
            content=full_response
        )

        # Redis同步
        await self.memory_manager.redis.add_message(
            conversation_id=conversation_id,
            role='user',
            content=question
        )

        await self.memory_manager.redis.add_message(
            conversation_id=conversation_id,
            role='assistant',
            content=full_response
        )

        await self.memory_manager.commit()

        # 第一条消息自动生成标题
        if len(history) == 0:
            await self.memory_manager.auto_update_title_from_first_message(
                conversation_id,
                question
            )


def build_chat_service(
        db: AsyncSession,
        role: str
):
    reids_memory = RedisMemory(
        redis_client=get_redis_client()
    )

    memory_manager = MemoryManager(
        db=db,
        redis_memory=reids_memory
    )

    message_service = MessageService(
        db=db
    )

    executor = ReActPlanExecutor(
        role=role
    )

    return ChatService(
        memory_manager=memory_manager,
        message_service=message_service,
        executor=executor
    )
