from fastapi import APIRouter, Depends, HTTPException

from pydantic import BaseModel

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.init_db import get_db

from app.auth.permissions import require_permission
from app.models.user import User

from app.services.conversation_service import ConversationService
from app.services.message_service import MessageService

from app.memory.redis_memory import RedisMemory
from app.redis.deps import get_redis_client, get_redis_memory

router = APIRouter(
    prefix="/conversations",
    tags=["会话管理"]
)


class UpdateTitleRequest(BaseModel):
    title: str


def get_conversation_service(
        db: AsyncSession
):
    return ConversationService(
        db=db,
        redis_memory=RedisMemory(get_redis_client)
    )


@router.post("")
async def create_conversation(
        current_user: User = require_permission("chat:create"),
        db: AsyncSession = Depends(get_db)
):
    service = get_conversation_service(db)
    conversation = await service.get_conversation(
        current_user.id
    )

    return {
        "id": conversation.id,
        'session_id': conversation.session_id,
        'title': conversation.title,
        'created_at': conversation.created_at
    }


@router.get("")
async def get_conversations(
        current_user: User = require_permission("chat:list"),
        db: AsyncSession = Depends(get_db)
):
    service = get_conversation_service(db)

    conversations = await service.get_list_conversation(current_user.id)
    return conversations


@router.get("/{conversation_id}")
async def get_conversation(
        conversation_id: int,
        current_user: User = require_permission("chat:list"),
        db: AsyncSession = Depends(get_db)
):
    service = get_conversation_service(db)
    conversation = await service.get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="会话不存在"
        )
    return conversation


@router.patch("/conversation_id")
async def update_title(
        conversation_id: int,
        request: UpdateTitleRequest,
        current_user: User = require_permission("chat:update"),
        db: AsyncSession = Depends(get_db)
):
    service = get_conversation_service(db)
    await service.update_title(conversation_id,
                               request.title)

    return {"message": "修改成功"}


@router.delete("/{conversation_id}")
async def delete_conversation(
        conversation_id: int,
        current_user: User =
        require_permission("chat:delete"),
        db: AsyncSession = Depends(get_db)
):
    service = get_conversation_service(db)

    success = service.delete_conversation(conversation_id)

    if not success:
        return HTTPException(
            status_code=404,
            detail="会话不存在"
        )
    return {
        "message": "删除成功"
    }


@router.get("/{conversation_id}/messages")
async def get_messages(
        conversation_id: int,
        page: int = 1,
        size: int = 50,

        current_user: User =
        require_permission("chat:list"),

        db: AsyncSession = Depends(get_db)
):
    service = MessageService(db)

    return await service.get_messages(
        conversation_id=conversation_id,
        page=page,
        size=size
    )
