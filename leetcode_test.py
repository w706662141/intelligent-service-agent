import os
from pathlib import Path

from langchain_core.documents import Document

from app.rag.vectorstore import load_qdrant_vectorstore

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "app" / "data"

# compress_docs = [Document(metadata={'source': 'e_commerce.txt',
#                                     'doc_id': 'e_commerce',
#                                     'doc_hash': '6b377ef661957bfb5f78756db0936e77', 'chunk_index': 115,
#                                     'chunk_id': 'e_commerce_chunk_115',
#                                     'chunk_hash': '5d8c672b8050b1f3469d3609261ea5e7',
#                                     'created_at': '2026-04-28T22:44:53.478124', 'bm25_score': 1.0,
#                                     'vector_score': 0.9873310868364262,
#                                     'hybrid_score': 0.9949324347345705, 'rank': 1, 'score_gap': 0.0},
#                           page_content='Q: 电子商务环境下物流的特点有哪些？\nA: 电子商务环境下物流的特点包括物流运作的特点，如信息化、自动化、网络化、智能化、柔性化，以及物品运输的特点，如多品种、小批量、多批次、短周期。')]
#
# for item in compress_docs:
#     if isinstance(item, tuple):
#         print(item[0])
vec = load_qdrant_vectorstore('rag_docs').embeddings.embed_query("测试一下")

print(vec is None)
print(type(vec))
print(len(vec) if vec else None)