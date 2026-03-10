from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List
from app.core.llm import get_model


def rag_answer(question: str, docs: List[Document]):
    """
    根据检索到的文档生成答案（RAG Answer 阶段）

    :param question: 用户问题
    :param docs: Retriever 返回的 Document 列表
    :return: 最终回答文本
    """

    # 1️⃣ 安全兜底（非常重要，防止空文档）
    if not docs:
        return "暂时没有查到相关信息，请联系人工客服。"

    # 2️⃣ 拼接上下文（Document → 纯文本）
    context = '\n\n'.join(
        f"[文档 {i + 1}]\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

    # 3️⃣ 构造 Answer Prompt（只允许基于资料回答）
    prompt = ChatPromptTemplate.from_template("""
    你是公司内部的智能助手，请根据给定的资料回答用户问题。
    如果资料中没有答案，请直接说“不确定”。
    
    资料：
    {context}
    
    用户问题：
    {question}
    
    回答：
    """)

    llm = get_model()

    chain = prompt | llm | StrOutputParser()

    # 5️⃣ 执行 Chain
    return chain.invoke({
        "context": context,
        "question": question
    }).strip()
