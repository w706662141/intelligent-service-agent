from typing import List

from pydantic import BaseModel, Field, field_validator


class RetrievedDoc(BaseModel):
    content: str
    score: float
    metadata: dict


class AnswerValidationInput(BaseModel):
    question: str
    answer: str = Field(min_length=5, max_length=2000)
    retrieved_docs: List[RetrievedDoc]

    @field_validator("retrieved_docs")
    @classmethod
    def must_have_docs(cls, v):
        if len(v) == 0:
            raise ValueError("No retrieved documents")
        return v
