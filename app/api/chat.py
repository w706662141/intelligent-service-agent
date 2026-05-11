from fastapi import APIRouter, Form
from pydantic import BaseModel

from app.agent.executor import ReActPlanExecutor

router = APIRouter()


pipeline = ReActPlanExecutor(role='admin')


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(question: str = Form(..., description="请输入你的问题")):
    answer = pipeline.run(question)
    # answer = agent.run(question)
    return {"answer": answer}
