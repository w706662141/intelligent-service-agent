from langchain_core.prompts import ChatPromptTemplate
from app.core.llm import get_model
from app.prompts.task.classifier import classify_question
from app.agent.retrievers import get_retriever_by_category
from app.query.query_rewriter import QueryRewriter
from app.rag.chain import build_rag_chain
from app.config.agent_log import log_event
from app.memory.short_memory import ShortTermMemory
from app.content.context_builder import enhance_question_with_memory
from app.compressors.vector_extractor import compress_document
from app.memory.context_pruner import ContextPruner
from app.validator.answer_validator import AnswerValidator


class MultiKBCustomerSupportAgent:

    def __init__(self) -> None:
        self.llm = get_model()
        self.memory = ShortTermMemory()
        self.pruner = ContextPruner(max_turns=5, max_chars=3000)

    def run(self, question: str) -> str:
        log_event(
            request_id='1',
            stage='user_input',
            question=question,
        )
        history = self.memory.get()
        prune_history = self.pruner.prune(history)

        log_event(
            request_id="1",
            stage="history_prune",
            before=len(history),
            after=len(prune_history)
        )

        enhanced_question = enhance_question_with_memory(
            question, history
        )
        category = classify_question(enhanced_question, self.llm)

        log_event(
            request_id='1',
            stage='classified',
            category=category,
        )
        if category == 'CHAT':
            return self.llm.invoke(question).content

        query_rewriter = QueryRewriter(self.llm)
        rewrite_result = query_rewriter.rewrite(enhanced_question)
        rewrite_question = rewrite_result.rewritten
        rewrite_reason = rewrite_result.reason
        log_event(
            request_id='1',
            stage='query_rewrite',
            original=question,
            rewritten=rewrite_question,
            reason=rewrite_reason
        )

        retriever = get_retriever_by_category(category)
        docs = retriever.retrieve(rewrite_question)

        if docs:
            log_event(
                request_id='1',
                stage='retriever',
                hit_docs=len(docs),
                scores=[
                    {
                        "bm25": d.metadata.get("bm25_score"),
                        "vector": d.metadata.get("vector_score"),
                        "hybrid": d.metadata.get("hybrid_score"),
                    }
                    for d in docs
                ],
                page_content=docs[0].page_content
            )

            compress_docs = compress_document(docs[0], rewrite_question, 20)

            log_event(
                request_id='1',
                stage='compressor',
                compress_docs=compress_docs[0].page_content
            )

            rag_chain = build_rag_chain(compress_docs, prune_history)
            answer = rag_chain.invoke(question).content

            self.memory.add("user", question)
            self.memory.add("assistant", answer)

            validator = AnswerValidator()
            retrieved_docs_for_validation = [
                {
                    "content": d.page_content,
                    "score": d.metadata.get("hybrid_score", 0.0),
                    "metadata": d.metadata
                }
                for d in compress_docs
            ]

            validation = validator.validate(
                question=rewrite_question,
                answer=answer,
                retrieved_docs=retrieved_docs_for_validation
            )

            log_event(
                request_id='1',
                stage='validator',
                validation_result=validation
            )

            if not validation["is_valid"]:
                return "抱歉，当前资料无法支持该问题，请联系人工客服。"
            return answer
        else:
            return self.llm.invoke(question).content


def need_retrieval(question: str) -> bool:
    """
    判断是否需要查询知识库
    """
    prompt = ChatPromptTemplate.from_template(
        """
        你是一个企业客服问题分类器。
        请判断用户问题是否需要查询内部知识库。
        
        如果是业务 / 产品 / 流程相关问题，回答 YES
        如果是闲聊 / 常识 / 问候，回答 NO
        
        用户问题：
        {question}
        
        只回答 YES 或 NO
        """
    )

    llm = get_model()

    resp = llm.invoke(
        prompt.format_messages(question=question)
    ).content.strip().upper()

    return resp == 'YES'
