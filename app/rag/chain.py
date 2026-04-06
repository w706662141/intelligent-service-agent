from langchain_core.runnables import RunnableLambda
from app.rag.fallback_policy import FALLBACK_POLICY
from app.router.intent_router import IntentRouter
from app.core.llm import get_model
from app.rag.answer import rag_answer
from app.prompts.builder import build_rag_prompt
from app.prompts.system.policy import POLICY_SYSTEM_PROMPT
from app.prompts.rag.rag_prompt import RAG_TASK_PROMPT


def format_docs(docs):
    if isinstance(docs, tuple):
        docs = [docs]

    formatted_contents = []
    for item in docs:
        doc = item[0] if isinstance(item, tuple) else item
        formatted_contents.append(doc.page_content)
    return '\n\n'.join(formatted_contents)


def format_history(history):
    """
    将对话历史格式化为 Prompt 可读文本
    注意：
    - 仅用于语义理解
    - 不作为事实依据
    """
    if not history:
        return "(无历史对话)"
    lines = []
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "").strip()

        if not content:
            continue
        if role == "user":
            lines.append(f"用户：{content}")
        elif role == "assistant":
            lines.append(f"助手:{content}")
        else:
            lines.append(f"{role}:{content}")

    return "\n".join(lines)


def build_rag_chain(docs, history):
    """
    构建标准 RAG Chain（LangChain 1.0 Runnable 写法）
    """

    llm = get_model()

    rag_chain = (
            RunnableLambda(
                lambda question: build_rag_prompt(
                    system_prompt=POLICY_SYSTEM_PROMPT.strip(),
                    task_prompt=RAG_TASK_PROMPT.strip(),
                    history=format_history(history=history),
                    docs=format_docs(docs=docs),
                    question=question
                )
            )
            | llm
    )

    return rag_chain
