import json

from app.core.llm import get_validator_model
from app.prompts.task.answer_judge import JUDGE_PROMPT


def llm_judge(question: str, answer: str, retrieved_docs: list):
    context = "\n\n".join([doc["content"] for doc in retrieved_docs])

    prompt = JUDGE_PROMPT.format(
        question=question,
        context=context,
        answer=answer,
    )

    response = get_validator_model().invoke(prompt)

    raw = response.content

    try:
        return json.loads(raw)
    except:
        return {
            "grounded": False,
            "hallucination": True,
            "policy_violation": False,
            "should_reject": True,
            "confidence": 0.0,
            "reason": "Judge解析失败"
        }
