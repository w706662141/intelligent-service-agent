from qdrant_client import QdrantClient
from app.config.settings import *

_client = None


def get_client():
    global _client

    if _client is None:
        _client = QdrantClient(
            host=QDRANT_HOST,
            port=QDRANT_PORT
        )

    return _client
