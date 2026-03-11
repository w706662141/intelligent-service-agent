from app.hybrid_score.hybrid_retriever import HybridRetriever


def build_hybrid_retriever(
        bm25_retriever,
        vector_retriever,
        bm25_weight=0.4,
        vector_weight=0.6,
        top_k=3,
        min_hybrid_score=0.6,
        top1_gap=0.15,
        doc_name=''
):
    return HybridRetriever(
        bm25_retriever=bm25_retriever,
        vectorstore=vector_retriever,
        w_bm25=bm25_weight,
        w_vector=vector_weight,
        top_k=top_k,
        min_hybrid_score=min_hybrid_score,
        top1_gap=top1_gap,
        doc_id=doc_name
    )
