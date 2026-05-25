from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app.content.context_builder import ContextRewriter
from app.core.llm import get_model, get_router_model

from app.agent.retrievers import get_retriever, get_retriever_by_category
from app.prompts.task.classifier import classify_question
from app.query.query_rewriter import QueryRewriter
from app.rag.chain import build_rag_chain
from app.config.agent_log import log_event
from app.compressors.vector_extractor import compress_document
from app.schemas.error import ErrorType
from app.schemas.result import ToolResult
from app.validator.answer_validator import AnswerValidator


class RagInput(BaseModel):
    """RAG 查询输入"""
    question: str = Field(description="用户问题，用于查询知识库")


@tool(args_schema=RagInput)
def rag_search(question: str, messages=None) -> dict:
    """
    用于查询企业知识库（文本类问题）。

    适用于：
    - 公司制度（报销流程、请假规则）
    - FAQ 与基础概念： 快速查询电子商务、网络营销、电子交易及电子支付的基本定义与核心概念（如：什么是“牛鞭效应”、电子支付的优势等） 。
    - 商业模式与战略分析： 包含对不同电商商业模式（B2B, B2C等）、战略规划工具（价值链分解、情境规划）及价值创造源泉的深度解析 。
    - 技术与法律文档说明： 涵盖互联网技术架构（TCP/IP, OSI模型）、新兴技术（物联网、云计算、大数据）以及《电子商务法》相关法律规范（如电子合同、知识产权） 。
    - 运营与供应链： 关于网络营销策略（4P/4C模型）、订单履行流程、第三方物流类型及供应链管理任务的专业指导

    不适用于：
    - 精确数值查询
    - 数据统计"""

    llm = get_model()

    if messages:
        context_rewriter = ContextRewriter(llm)
        question = context_rewriter.rewrite(question, messages)

        log_event(
            request_id='1',
            stage='context_rewrite',
            rewritten=question
        )

    query_rewriter = QueryRewriter(llm)
    rewrite_result = query_rewriter.rewrite(question)
    rewrite_question = rewrite_result.rewritten
    rewrite_reason = rewrite_result.reason

    log_event(
        request_id='1',
        stage='query_rewrite',
        original=question,
        rewritten=rewrite_question,
        reason=rewrite_reason,
        tool="rag_search_tool"
    )

    category = classify_question(rewrite_question, get_router_model())

    # retriever = get_retriever(category)
    retriever = get_retriever_by_category(category)
    docs = retriever.retrieve(rewrite_question)
    print('docs', docs)
    if not docs:
        return ToolResult(
            success=False,
            error_type=ErrorType.NOT_FOUND,
            message="未检索到相关信息",
        ).to_dict()

    # 压缩
    compress_docs = []
    for doc in docs[:3]:
        compress_docs.extend(
            compress_document(doc, rewrite_question, 100)
        )
    # compress_docs = compress_document(docs[0], rewrite_question, 20)
    print('compress_docs', compress_docs)
    # RAG生成
    rag_chain = build_rag_chain(compress_docs, [])
    answer = rag_chain.invoke(question).content
    print('answer', answer)
    # 校验
    validator = AnswerValidator()
    validation = validator.validate(
        question=rewrite_question,
        answer=answer,
        retrieved_docs=[
            {
                "content": d.page_content,
                "score": d.metadata.get("hybrid_score", 0.0),
                "metadata": d.metadata
            }
            for d in compress_docs
        ]
    )
    print('validation', validation)
    if not validation['is_valid']:
        return ToolResult(
            success=False,
            error_type=ErrorType.NOT_FOUND,
            message="当前资料无法支持该问题",
        ).to_dict()

    return ToolResult(
        success=True,
        error_type=ErrorType.NONE,
        message="查询成功",
        data=dict({"answer": answer})
    ).to_dict()
