from pathlib import Path

from app.hybrid_score.bm25_okapi_retriever import BM25OkapiRetriever
from app.config.collection_name_urls import get_collection_path
from app.vector_store.load_chunks import QdrantChunkLoader
from app.vector_store.qdrant_client import get_client

_BM25_CACHE = {}
# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_PATH = BASE_DIR / "data" / "hr_policy.txt"

client = get_client()


def prepare_chunks(file_url: str):
    loader = QdrantChunkLoader(
        client=client,
        collection_name='rag_docs',
        text_field='page_content'
    )
    chunks = loader.load_chunks()
    return chunks


def get_bm25_retriever(collection_name: str, chunks, k: int = 3):
    """
    BM25 进程级缓存
    """
    if collection_name not in _BM25_CACHE:
        if not chunks:
            file_url = get_collection_path(collection_name)
            chunks = prepare_chunks(str(file_url))

        retriever = BM25OkapiRetriever(
            documents=chunks,
            top_k=k
        )

        _BM25_CACHE[collection_name] = retriever

    return _BM25_CACHE[collection_name]
