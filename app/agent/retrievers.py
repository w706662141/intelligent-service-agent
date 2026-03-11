from app.rag.vectorstore import  load_qdrant_vectorstore
from app.hybrid_score.bm25 import get_bm25_retriever
from app.rag.store import get_hr_chunks, get_faq_chunks, get_tech_chunks
from app.hybrid_score.hybrid import build_hybrid_retriever


def get_hr_retriever():
    vector = load_qdrant_vectorstore("rag_docs")
    # HR_CHUNKS = get_hr_chunks()
    bm25 = get_bm25_retriever("hr_kb", "", k=3)

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name='hr_policy'
    )


def get_tech_retriever():
    # vector = load_chroma_vectorstore("tech_kb")
    vector = load_qdrant_vectorstore("rag_docs")
    TECH_CHUNKS = get_tech_chunks()
    bm25 = get_bm25_retriever('tech_kb', TECH_CHUNKS, k=3)

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        bm25_weight=0.5,
        vector_weight=0.5,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name='tech_support'
    )


def get_faq_retriever():
    # vector = load_chroma_vectorstore('faq_kb')
    vector = load_qdrant_vectorstore('rag_docs')
    FAQ_CHUNKS = get_faq_chunks()
    bm25 = get_bm25_retriever('faq_kb', FAQ_CHUNKS, k=3)

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        bm25_weight=0.4,
        vector_weight=0.6,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name='faq'
    )


class RejectRetriever:
    def retirever(self, query: str):
        return []


def get_retriever_by_category(category: str):
    """
    根据问题分类返回对应 retriever
    """
    if category == 'FAQ':
        return get_faq_retriever()
    elif category == 'HR':
        return get_hr_retriever()
    elif category == 'TECH':
        return get_tech_retriever()
    else:
        return RejectRetriever()
