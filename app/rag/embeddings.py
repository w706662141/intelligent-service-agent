from langchain_huggingface import HuggingFaceEmbeddings
from threading import Lock

_embedding = None
_embedding_lock = Lock()


def get_embeddings():
    global _embedding
    if not _embedding:
        with _embedding_lock:
            if not _embedding:
                _embedding = HuggingFaceEmbeddings(
                    # model_name="BAAI/bge-m3",
                    model_name="BAAI/bge-large-zh",
                    encode_kwargs={"normalize_embeddings": True}
                )

    return _embedding
