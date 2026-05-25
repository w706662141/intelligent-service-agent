from app.rag.vectorstore import load_qdrant_vectorstore
from app.hybrid_score.bm25 import get_bm25_retriever
from app.rag.store import get_hr_chunks, get_faq_chunks, get_tech_chunks, get_rag_collection_chunks
from app.hybrid_score.hybrid import build_hybrid_retriever
from app.core.reranker import get_reranker_model

reranker = get_reranker_model()


def get_rag_collection_retriever(doc_name):
    vector = load_qdrant_vectorstore('rag_docs')
    RAG_COLLECTION_CHUNKS = get_rag_collection_chunks()
    bm25 = get_bm25_retriever(RAG_COLLECTION_CHUNKS, k=3, collection_name='rag_docs')

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        reranker=reranker,
        top_k=5,
        vector_k=5,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=doc_name,
        rrf_k=10,
        recall_k=3,

    )


def get_hr_retriever(doc_name):
    vector = load_qdrant_vectorstore("rag_docs")
    RAG_COLLECTION_CHUNKS = get_rag_collection_chunks()
    bm25 = get_bm25_retriever(RAG_COLLECTION_CHUNKS, k=3, collection_name='rag_docs')

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        reranker=reranker,
        top_k=5,
        vector_k=5,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=doc_name,
        rrf_k=10,
        recall_k=3,

    )


def get_tech_retriever(doc_name):
    # vector = load_chroma_vectorstore("tech_kb")
    vector = load_qdrant_vectorstore("rag_docs")
    RAG_COLLECTION_CHUNKS = get_rag_collection_chunks()
    bm25 = get_bm25_retriever(RAG_COLLECTION_CHUNKS, k=3, collection_name='rag_docs')

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        reranker=reranker,
        top_k=5,
        vector_k=5,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=doc_name,
        rrf_k=10,
        recall_k=3,

    )


def get_faq_retriever(doc_name):
    # vector = load_chroma_vectorstore('faq_kb')
    vector = load_qdrant_vectorstore('rag_docs')
    RAG_COLLECTION_CHUNKS = get_rag_collection_chunks()
    bm25 = get_bm25_retriever(RAG_COLLECTION_CHUNKS, k=3, collection_name='rag_docs')

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        reranker=reranker,
        top_k=5,
        vector_k=5,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=doc_name,
        rrf_k=10,
        recall_k=3,

    )


def get_e_commerce_retriever(doc_name):
    vector = load_qdrant_vectorstore('rag_docs')
    RAG_COLLECTION_CHUNKS = get_rag_collection_chunks()
    bm25 = get_bm25_retriever(RAG_COLLECTION_CHUNKS, k=3, collection_name='rag_docs')

    return build_hybrid_retriever(
        bm25_retriever=bm25,
        vector_retriever=vector,
        reranker=reranker,
        top_k=5,
        vector_k=5,
        bm25_weight=0.6,
        vector_weight=0.4,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=doc_name,
        rrf_k=10,
        recall_k=3,
    )


class RejectRetriever:
    def retirever(self, query: str):
        return []


def get_retriever_by_category(category: str):
    """
    根据问题分类返回对应 retriever
    """
    if category == 'FAQ':
        return get_faq_retriever(category)
    elif category == 'HR':
        return get_hr_retriever(category)
    elif category == 'TECH':
        return get_tech_retriever(category)
    elif category == 'E-COMMERCE':
        return get_e_commerce_retriever(category)
    else:
        return RejectRetriever()


def get_retriever(doc_name):
    return get_rag_collection_retriever(doc_name)
