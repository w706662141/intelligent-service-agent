from typing import List, Dict
from langchain_core.documents import Document
import numpy as np
import logging
from app.config.agent_log import log_event
from qdrant_client.models import Filter,FieldCondition,MatchValue
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
            doc_id:str=''

    ) -> None:
        self.bm25 = bm25_retriever
        self.vectorstore = vectorstore
        self.w_bm25 = w_bm25
        self.w_vector = w_vector
        self.top_k = top_k
        self.vector_k = vector_k
        self.min_hybrid_score = min_hybrid_score
        self.top1_gap = top1_gap
        self.doc_id=doc_id

    def __call__(self, query: str):
        return self.retrieve(query)

    # ========================
    # 公共入口（你在 router / agent 里调用这个）
    # ========================

    def retrieve(self, query: str) -> List[Document]:
        bm25_docs = self._bm25_search(query)
        vector_docs = self._vector_search(query)

        merged = self._merge_results(bm25_docs, vector_docs)
        scored = self._score_fusion(merged)
        ranked = self._rank(scored)

        return ranked

    # def invoke(self, query: str):
    #     return self.retrieve(query)

    # ========================
    # BM25
    # ========================
    def _bm25_search(self, query: str) -> List[Document]:
        docs = self.bm25.invoke(query)

        for d in docs:
            if "bm25_score" not in d.metadata:
                raise ValueError("BM25 document missing bm25_score in metadata")

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

        docs = self.vectorstore.similarity_search_with_relevance_scores(
            query,
            k=self.vector_k,
            filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.doc_id",
                        match=MatchValue(value="hr_policy")
                    )
                ]
            )
        )
        logger.debug(f"[HybridRetriever] Vector docs={len(docs)}")
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

    # ========================
    # 排序 + 阈值
    # ========================
    def _rank(self, scored: List[Dict]) -> List[Document]:
        scored.sort(key=lambda x: x["hybrid_score"], reverse=True)

        for item in scored:
            log_event(
                request_id='1',
                stage='hybrid_rank',
                bm25=item["bm25_norm"],
                vector=item["vector_norm"],
                hybrid=item["hybrid_score"]
            )

        results = []
        # 2️⃣ 取 Top1 / Top2 做决策
        top1 = scored[0]
        top2 = scored[1] if len(scored) > 1 else None

        top1_score = top1.get('hybrid_score', 0.0)
        top2_score = top1.get('hybrid_score', 0.0) if top2 else 0.0

        if top1_score < self.min_hybrid_score:
            print(f"[RAG] Top1 score too low: {top1_score:.4f}")
            return []
        # if top2 and (top1_score - top2_score) < self.top1_gap:
        #     print(
        #         f"[RAG] Top1 gap too small: "
        #         f"{top1_score:.4f} vs {top2_score:.4f}"
        #     )
        #     return []

        # 4️⃣ 只返回 Top1（客服场景）
        item = top1
        doc = item['doc']

        bm25 = item.get("bm25_norm", 0.0)
        vector = item.get("vector_norm", 0.0)
        hybrid = item.get("hybrid_score", 0.0)

        # print(
        #     f"bm25={bm25:.4f} | "
        #     f"vector={vector:.4f} | "
        #     f"hybrid={hybrid:.4f}"
        # )

        # 5️⃣ 写入 metadata（调试 + 可解释性）
        doc.metadata.update({
            "bm25_score": bm25,
            "vector_score": vector,
            "hybrid_score": hybrid,
        })

        return [doc]

    @staticmethod
    def _normalize(scores: np.ndarray) -> np.ndarray:
        if len(scores) == 0:
            return scores

        min_v = scores.min()
        max_v = scores.max()

        if max_v == min_v:
            return np.ones_like(scores)
        return (scores - min_v) / (max_v - min_v)
