import json
from typing import Optional, List

from fastapi import APIRouter, Form, Query, Header, Depends
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from app.agent.executor import ReActPlanExecutor
from app.auth.jwt import create_token
from app.auth.permissions import require_permission
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.init_db import get_db
from app.services.chat_service import ChatService, build_chat_service
from app.memory.memory_manager import MemoryManager
from app.services.message_service import MessageService

router = APIRouter(
    prefix="/chat",
    tags=["Chat"])


# ==================== 请求模型 ====================

class DeleteMessagesRequest(BaseModel):
    message_ids: Optional[List[int]] = None


class UpdateSessionTitleRequest(BaseModel):
    title: str


@router.post('/stream')
def chat_stream(
        question: str = Form(..., description="请输入你的问题"),
        conversation_id: int = Form(...),
        current_user: User = require_permission("chat:stream"),
        db: AsyncSession = Depends(get_db)
):
    role = current_user.roles[0].name if current_user.roles else "user"
    chat_service = build_chat_service(db, role)

    async def event_generator():
        for chunk in chat_service.chat(conversation_id, question):
            # SSE 格式：data: xxx\n\n
            yield f"data:" \
                  f"{json.dumps({'content': chunk}, ensure_ascii=False)}" \
                  f"\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache",
                 "X-Accel-Buffering": "no"},

    )


@router.post("/token")
def get_token(user_id: str = Query(...), role: str = Query(default="user")):
    """模拟签发 token（测试用，正式环境由认证服务提供）"""
    token = create_token(user_id, role)
    return {"token": token, "user_id": user_id, "role": role}
