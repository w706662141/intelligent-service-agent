from pydantic import ValidationError

from app.validator.llm_answer_judge import llm_judge
from app.validator.validation_schema import AnswerValidationInput


class AnswerValidator:
    def __init__(self, use_llm_judge=True):
        self.use_llm_judge = use_llm_judge

    def validate(self, question, answer, retrieved_docs):
        # 1️⃣ Pydantic 基础校验

        try:
            AnswerValidationInput(
                question=question,
                answer=answer,
                retrieved_docs=retrieved_docs
            )
        except ValidationError as e:
            return {
                "is_valid": False,
                "stage": "schema",
                "reason": str(e)
            }
        # 2️⃣ LLM Judge
        if self.use_llm_judge:
            judge_result = llm_judge(question, answer, retrieved_docs)

            if judge_result["should_reject"]:
                return {
                    "is_valid": False,
                    "stage": "llm_judge",
                    "reason": judge_result["reason"],
                    "confidence": judge_result["confidence"]
                }
            return {
                "is_valid": True,
                "confidence": judge_result["confidence"],
                "reason": judge_result["reason"]
            }

        return {"is_valid": True}
