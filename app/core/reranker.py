from sentence_transformers import CrossEncoder


class BGEReranker:

    def __init__(self, model_name='BAAI/bge-reranker-base'):
        self.model = CrossEncoder(model_name)

    def rerank(self, query, docs):
        pairs = [(query, doc.page_content) for doc in docs]
        scores = self.model.predict(pairs)

        for doc, score in zip(docs, scores):
            doc.metadata['rerank_score'] = float(score)

        docs.sort(key=lambda x: x.metadata['rerank_score'], reverse=True)

        return docs


_reranker_model = None


def get_reranker_model():
    global _reranker_model
    if not _reranker_model:
        _reranker_model = BGEReranker()

    return _reranker_model
