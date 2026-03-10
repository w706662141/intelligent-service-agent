from pathlib import Path
from app.file_kb.loader import load_docs
from app.hybrid_score.bm25_okapi_retriever import BM25OkapiRetriever
from app.file_kb.splitter import split_docs
from app.config.collection_name_urls import get_collection_path

_BM25_CACHE = {}
# BASE_DIR = Path(__file__).resolve().parent.parent
# DATA_PATH = BASE_DIR / "data" / "hr_policy.txt"


def prepare_chunks(file_url: str):
    docs = load_docs(str(file_url))
    chunks = split_docs(docs)
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
