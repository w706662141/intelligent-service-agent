from fastapi import APIRouter, Depends, Form, Query, Header
from pydantic import BaseModel

from app.auth.jwt import create_token, verify_token
from app.memory.session_manager import SessionManager

router = APIRouter()

session_manager = SessionManager(expire_seconds=1800)


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(
    question: str = Form(..., description="请输入你的问题"),
    session_id: str = Header(..., alias="X-Session-Id", description="会话ID"),
    token_payload: dict = Depends(verify_token),
):
    user_id = token_payload["sub"]
    role = token_payload.get("role", "user")

    session = session_manager.get_or_create(user_id, session_id, role)
    answer = session.executor.run(question)
    return {"answer": answer}


@router.post("/token")
def get_token(user_id: str = Query(...), role: str = Query(default="user")):
    """模拟签发 token（测试用，正式环境由认证服务提供）"""
    token = create_token(user_id, role)
    return {"token": token, "user_id": user_id, "role": role}


@router.delete("/session")
def clear_session(
    session_id: str = Header(..., alias="X-Session-Id"),
    token_payload: dict = Depends(verify_token),
):
    user_id = token_payload["sub"]
    removed = session_manager.remove(user_id, session_id)
    return {"user_id": user_id, "session_id": session_id, "cleared": removed}
