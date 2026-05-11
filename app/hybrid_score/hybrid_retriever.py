from typing import List, Dict
from langchain_core.documents import Document
import numpy as np
import logging
from app.config.agent_log import log_event
from qdrant_client.models import Filter, FieldCondition, MatchValue

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Score-based Hybrid Retriever
    BM25 + Vector similarity with explicit score fusion
    """

    def __init__(
            self,
            bm25_retriever,
            vectorstore,
            *,
            w_bm25: float = 0.4,
            w_vector: float = 0.6,
            top_k: int = 3,
            vector_k: int = 3,
            min_hybrid_score: float | None = None,
            top1_gap: float = 0.15,
            doc_id: str = '',
            reranker=None,
            rrf_k=20,
            recall_k=3,

    ) -> None:
        self.bm25 = bm25_retriever
        self.vectorstore = vectorstore
        self.w_bm25 = w_bm25
        self.w_vector = w_vector
        self.top_k = top_k
        self.vector_k = vector_k
        self.min_hybrid_score = min_hybrid_score
        self.top1_gap = top1_gap
        self.doc_id = doc_id
        self.reranker = reranker
        self.rrf_k = rrf_k
        self.recall_k = recall_k

    def __call__(self, query: str):
        return self.retrieve(query)

    # ========================
    # 公共入口（你在 router / agent 里调用这个）
    # ========================

    def retrieve(self, query: str) -> List[Document]:
        bm25_docs = self._bm25_search(query)
        vector_docs = self._vector_search(query)

        print('bm25_docs', bm25_docs)
        print('vector_docs_result', vector_docs)

        # merged = self._merge_results(bm25_docs, vector_docs)
        # scored = self._score_fusion(merged)
        # ranked = self._rank(scored)

        # 合并 + RRF
        candidates = self._rrf_fusion(bm25_docs, vector_docs)
        # 3️⃣ 截断候选
        candidates = candidates[:self.recall_k]
        # 4️⃣ rerank（关键）
        if self.reranker:
            candidates = self._rerank(query, candidates)

        print('candidates', candidates[:self.top_k])

        return candidates[:self.top_k]

    # def invoke(self, query: str):
    #     return self.retrieve(query)

    # ========================
    # BM25
    # ========================
    def _bm25_search(self, query: str) -> List[Document]:
        docs = self.bm25.invoke(query)

        for i, d in enumerate(docs):
            if "bm25_score" not in d.metadata:
                raise ValueError("BM25 document missing bm25_score in metadata")
            d.metadata['bm25_rank'] = i + 1

        logger.debug(f"[HybridRetriever] BM25 docs={len(docs)}")
        return docs

    # ========================
    # Vector
    # ========================

    def _vector_search(self, query: str):
        """
        similarity_search_with_score
        return: List[(Document, score)]
        """
        print('query', query)
        docs_with_scores = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=self.vector_k,
        )
        logger.debug(f"[HybridRetriever] Vector docs={len(docs_with_scores)}")

        docs = []
        for i, (doc, score) in enumerate(docs_with_scores):
            doc.metadata['vector_score'] = score
            doc.metadata['vector_rank'] = i + 1
            docs.append(doc)

        return docs

    # ========================
    # 合并结果（按 chunk_id / doc_id）
    # ========================

    def _merge_results(
            self,
            bm25_docs: List[Document],
            vector_docs_with_score
    ) -> Dict[str, Dict]:
        results: Dict[str, Dict] = {}

        def get_doc_id(doc: Document) -> str:
            return doc.metadata.get('chunk_id') or \
                   doc.metadata.get('doc_id')

        # BM25
        for doc in bm25_docs:
            doc_id = get_doc_id(doc)
            results.setdefault(doc_id, {
                'doc': doc,
                'bm25': 0.0,
                'vector': 0.0
            })
            results[doc_id]['bm25'] = doc.metadata['bm25_score']

        # Vector
        for doc, score in vector_docs_with_score:
            doc_id = get_doc_id(doc)
            results.setdefault(doc_id, {
                "doc": doc,
                "bm25": 0.0,
                "vector": 0.0
            })
            results[doc_id]["vector"] = score

        return results

    # ========================
    # 分数融合（归一化 + 加权）
    # ========================

    def _score_fusion(self, results: Dict[str, Dict]) -> List[Dict]:
        bm25_scores = np.array([v["bm25"] for v in results.values()])
        vector_scores = np.array([v["vector"] for v in results.values()])

        bm25_norm = self._normalize(bm25_scores)
        vector_norm = self._normalize(vector_scores)

        print('bm25_norm', bm25_norm)
        print('vector_norm', vector_norm)

        fused = []
        for (doc_id, v), b_score, v_score in zip(
                results.items(), bm25_norm, vector_norm
        ):
            hybrid_score = self.w_bm25 * b_score + self.w_vector * v_score

            v["bm25_norm"] = float(b_score)
            v["vector_norm"] = float(v_score)
            v["hybrid_score"] = float(hybrid_score)

            fused.append(v)
        return fused

    def _rank(self, scored: List[Dict]) -> List[Document]:
        scored.sort(key=lambda x: x['hybrid_score'], reverse=True)

        for item in scored:
            log_event(
                request_id='1',
                stage='hybrid_rank',
                bm25=item["bm25_norm"],
                vector=item["vector_norm"],
                hybrid=item["hybrid_score"]
            )

        if not scored:
            return []

        top1_score = scored[0].get('hybrid_score', 0.0)

        if top1_score < self.min_hybrid_score:
            print(f"[RAG] Top1 score too low: {top1_score:.4f} < {self.min_hybrid_score}")
            return []

        actual_top_k = min(self.top_k, len(scored))

        results = []

        for i in range(actual_top_k):
            item = scored[i]
            current_score = item.get('hybrid_score', 0.0)
            score_gap = top1_score - current_score

            if score_gap >= self.top1_gap or current_score < self.min_hybrid_score:
                print(f"[RAG] Doc at rank {i + 1} filtered due to score gap or 小于 min_score: "
                      f"{current_score:.4f} (gap: {score_gap:.4f} > {self.top1_gap},"
                      f"min_score:{self.min_hybrid_score})")
                break  # 一旦遇到差距过大的，后面的也就不用检查了

            doc = item['doc']
            bm25 = item.get("bm25_norm", 0.0)
            vector = item.get("vector_norm", 0.0)
            hybrid = item.get("hybrid_score", 0.0)

            doc.metadata.update({
                "bm25_score": bm25,
                "vector_score": vector,
                "hybrid_score": hybrid,
                "rank": len(results) + 1,
                "score_gap": score_gap,
            })

            results.append(doc)
        print(f"[RAG] Returning {len(results)} documents (requested top_{self.top_k})")
        return results

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        if len(scores) == 0:
            return scores

        min_v = scores.min()
        max_v = scores.max()

        if max_v == min_v:
            return np.ones_like(scores)
        return (scores - min_v) / (max_v - min_v)

    def _rrf(self, rank):
        return 1 / (self.rrf_k + rank)

    def _rrf_fusion(self, bm25_docs, vector_docs):

        results = {}

        def get_id(doc):
            return doc.metadata.get('chunk_id') or doc.metadata.get('doc_id')

        # bm25
        for doc in bm25_docs:
            doc_id = get_id(doc)
            results.setdefault(doc_id, {
                'doc': doc,
                'bm25_rank': None,
                'vector_rank': None
            })

            results[doc_id]['bm25_rank'] = doc.metadata['bm25_rank']

        # vector
        for doc in vector_docs:
            doc_id = get_id(doc)
            results.setdefault(doc_id, {
                'doc': doc,
                'bm25_rank': None,
                'vector_rank': None
            })

            results[doc_id]['vector_rank'] = doc.metadata['vector_rank']

        # 👉 计算 RRF 分数
        fused = []

        for item in results.values():
            score = 0.0

            if item['bm25_rank']:
                score += self._rrf(item['bm25_rank'])

            if item['vector_rank']:
                score += self._rrf(item['vector_rank'])

            item['score'] = score
            fused.append(item)

        # 排序
        fused.sort(key=lambda x: x['score'], reverse=True)

        return [x['doc'] for x in fused]

    def _rerank(self, query, docs):
        return self.reranker.rerank(query, docs)
