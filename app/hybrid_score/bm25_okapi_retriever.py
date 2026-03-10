from typing import List

import jieba
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi


class BM25OkapiRetriever:

    def __init__(self, documents: List[Document], top_k: int = 3) -> None:
        self.documents = documents
        self.top_k = top_k

        self.texts = [d.page_content for d in documents]
        self.metadatas = [d.metadata for d in documents]

        tokenized_corpus = [jieba.lcut(t) for t in self.texts]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def invoke(self, query: str) -> List[Document]:
        tokenized_query = jieba.lcut(query)
        scores = self.bm25.get_scores(tokenized_query)

        ranked = sorted(
            enumerate(scores),
            key=lambda x: x[1],
            reverse=True
        )[:self.top_k]

        results = []
        for idx, score in ranked:
            doc = Document(
                page_content=self.texts[idx],
                metadata=dict(self.metadatas[idx])
            )

            doc.metadata['bm25_score'] = float(max(score, 0.0))
            results.append(doc)

        return results
