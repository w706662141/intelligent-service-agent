from app.rag.vectorstore import load_chroma_vectorstore


def retriever_with_threshold(
        question: str,
        collection_name: str,
        top_k: int = 3,
        score_threshold: float = 0.6
):
    """
    返回满足阈值的 docs
    score 越小 = 越相似（Chroma 默认是距离）
    """

    vs = load_chroma_vectorstore(collection_name=collection_name)

    results = vs.similarity_search_with_relevance_scores(question, k=top_k)
    passed_docs = []

    for doc, score in results:
        if score >= score_threshold:
            passed_docs.append(doc)

    return passed_docs, results
