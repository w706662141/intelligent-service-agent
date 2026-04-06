from typing import List, Dict
from app.prompts.rag.rag_prompt import RAG_CONTEXT_REWRITER_PROMPT


def format_history_for_llm(history: List[Dict]):
    """
    将历史对话转为模型可理解的上下文描述
    """

    if not history:
        return ""

    lines = []

    for h in history:
        role = "用户" if h['role'] == 'user' else '助手'
        lines.append(f"{role}:{h['content']}")

    return "\n".join(lines)


def enhance_question_with_memory(
        question: str,
        history: List[Dict]
):
    """
    在不污染原问题的情况下增强上下文
    """

    if not history:
        return question

    history_text = format_history_for_llm(history)
    return f"""
    以下是最近的对话背景，请结合理解用户当前问题：
    {history_text}
    当前用户问题：
    {question}
    """.strip()


class ContextRewriter:
    def __init__(self, llm):
        self.llm = llm
        self.prompt = RAG_CONTEXT_REWRITER_PROMPT

    def rewrite(self, question, messages):
        history = "\n".join([
                                m.content for m in messages if hasattr(m, "content")
                            ][-4:])

        chain = self.prompt | self.llm

        return chain.invoke({
            "history": history,
            "question": question
        }).content.strip()
