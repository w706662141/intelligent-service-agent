from app.hybrid_score.bm25_okapi_retriever import BM25OkapiRetriever
from app.config.collection_name_urls import get_collection_path
from app.vector_store.load_chunks import QdrantChunkLoader
from app.vector_store.qdrant_client import get_client
from threading import Lock

_BM25_CACHE = {}
_BM25_LOCKS = {}
_CACHE_GLOBAL_LOCK = Lock()


def _get_lock(collection_name: str) -> Lock:
    if collection_name not in _BM25_LOCKS:
        with _CACHE_GLOBAL_LOCK:
            if collection_name not in _BM25_LOCKS:
                _BM25_LOCKS[collection_name] = Lock()
    return _BM25_LOCKS[collection_name]


def prepare_chunks(file_url: str):
    loader = QdrantChunkLoader(
        client=get_client(),
        collection_name='rag_docs',
        text_field='page_content'
    )
    chunks = loader.load_chunks()
    return chunks


def get_bm25_retriever(chunks, k: int = 3, collection_name: str = 'default'):
    """
    BM25 进程级缓存
    """
    if collection_name not in _BM25_CACHE:
        lock = _get_lock(collection_name)
        with lock:
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
