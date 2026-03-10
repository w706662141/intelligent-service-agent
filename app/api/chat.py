from fastapi import APIRouter, Form
from pydantic import BaseModel

from app.agent.agent import MultiKBCustomerSupportAgent

router = APIRouter()

agent = MultiKBCustomerSupportAgent()


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
def chat(question: str = Form(..., description="请输入你的问题")):
    answer = agent.run(question)
    return {"answer": answer}
