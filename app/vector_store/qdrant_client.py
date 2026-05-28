from qdrant_client import QdrantClient
from app.config.settings import *
from threading import Lock

_client = None
_qdrant_client_lock = Lock()


def get_client():
    global _client

    if _client is None:
        with _qdrant_client_lock:
            if _client is None:
                _client = QdrantClient(
                    host=QDRANT_HOST,
                    port=QDRANT_PORT,
                    timeout=60
                )

    return _client
