import json

from fastapi import APIRouter, Depends, Form, Query, Header
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

from app.auth.jwt import create_token
from app.auth.permissions import require_permission
from app.models.user import User
from app.memory.session_manager import SessionManager

router = APIRouter()

session_manager = SessionManager(expire_seconds=1800)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(
        question: str = Form(..., description="请输入你的问题"),
        session_id: str = Header(..., alias="X-Session-Id", description="会话ID"),
        current_user: User = require_permission("chat:send"),
):
    user_id = str(current_user.id)
    role = current_user.roles[0].name if current_user.roles else "user"

    session = session_manager.get_or_create(user_id, session_id, role)
    answer = session.executor.run(question)
    return {"answer": answer}


@router.post('/chat/stream')
def chat_stream(
        question: str = Form(..., description="请输入你的问题"),
        session_id: str = Header(..., alias="X-Session-Id", description="会话ID"),
        current_user: User = require_permission("chat:stream"),
):
    user_id = str(current_user.id)
    role = current_user.roles[0].name if current_user.roles else "user"

    session = session_manager.get_or_create(user_id, session_id, role)

    def event_generator():
        for chunk in session.executor.run(question):
            # SSE 格式：data: xxx\n\n
            yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},

    )


@router.post("/token")
def get_token(user_id: str = Query(...), role: str = Query(default="user")):
    """模拟签发 token（测试用，正式环境由认证服务提供）"""
    token = create_token(user_id, role)
    return {"token": token, "user_id": user_id, "role": role}


@router.delete("/session")
def clear_session(
        session_id: str = Header(..., alias="X-Session-Id"),
        current_user: User = require_permission("session:manage"),
):
    user_id = str(current_user.id)
    removed = session_manager.remove(user_id, session_id)
    return {"user_id": user_id, "session_id": session_id, "cleared": removed}
