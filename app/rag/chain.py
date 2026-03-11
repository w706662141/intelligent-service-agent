from langchain_core.runnables import  RunnableLambda
from app.rag.fallback_policy import FALLBACK_POLICY
from app.router.intent_router import IntentRouter
from app.core.llm import get_model
from app.rag.answer import rag_answer
from app.prompts.builder import build_rag_prompt
from app.prompts.system.policy import POLICY_SYSTEM_PROMPT
from app.prompts.rag.rag_prompt import RAG_TASK_PROMPT


def format_docs(docs):
    return '\n\n'.join(doc.page_content for doc in docs)


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

    # prompt = ChatPromptTemplate.from_template("""
    # 你是企业内部制度问答助手。
    #
    # 【回答规则（必须严格遵守）】
    # 1. 只允许使用【已知信息】中的内容作答
    # 2. 不得补充、推测、延伸任何未出现的信息
    # 3. 不得引入个人经验、常识判断或额外建议
    # 4. 不得向用户提出反问或额外要求
    # 5. 尽量使用【已知信息】中的原文表述，可在不改变含义的前提下做最小整理
    # 6. 如果【已知信息】不足以回答当前问题，必须回答：
    #    未在知识库中找到相关规定
    #
    # 【对话上下文（用于理解问题背景，不等同于已知信息）】
    # 以下为用户与系统的历史对话，仅用于理解当前问题中的指代、省略或上下文含义，
    # 不得作为回答依据引用其中的信息：
    #
    # {history}
    #
    # 【已知信息（唯一可作为回答依据的内容）】
    # {context}
    #
    # 【用户问题】
    # {question}
    # """)

    # llm = get_model()
    #
    # rag_chain = (
    #         {
    #             "context": RunnableLambda(lambda _: format_docs(docs)),
    #             "question": RunnablePassthrough(),
    #             "history": RunnableLambda(lambda _: format_history(history))
    #         }
    #         | prompt
    #         | llm
    # )

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
