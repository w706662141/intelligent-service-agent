import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance

from langchain_qdrant import QdrantVectorStore
from app.rag.embeddings import get_embeddings

from app.config.settings import (
    QDRANT_URL,
    QDRANT_VECTOR_SIZE,
    COLLECTION_NAME
)


class QdrantStore:

    def __init__(self):
        self.client = QdrantClient(url=QDRANT_URL)
        self._create_collection()
        self._create_payload_indexs()
        self.embeddings = get_embeddings()

        self.vector_store = QdrantVectorStore(
            client=self.client,
            collection_name=COLLECTION_NAME,
            embedding=self.embeddings
        )

    def _create_collection(self):
        collections = self.client.get_collections().collections

        names = [c.name for c in collections]

        if COLLECTION_NAME not in names:
            self.client.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=VectorParams(
                    size=QDRANT_VECTOR_SIZE,
                    distance=Distance.COSINE
                )
            )

    def _create_payload_indexs(self):
        self.client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name='doc_id',
            field_schema='keyword'
        )

        self.client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name='chunk_id',
            field_schema='keyword'
        )
        self.client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name='source',
            field_schema='keyword'
        )

    def get_existing_chunks(self, doc_id):
        result = self.client.scroll(
            collection_name=COLLECTION_NAME,
            scroll_filter={
                'must': [
                    {
                        'key': 'doc_id',
                        'match': {'value': doc_id}
                    }
                ]
            },
            limit=10000
        )

        points = result[0]

        existing = {}

        for p in points:
            payload = p.payload

            existing[payload['chunk_id']] = payload['chunk_hash']

        return existing

    def delete_chunks(self, ids):

        if not ids:
            return

        self.client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=ids
        )

    def upsert_chunks(self, chunks):
        ids = [str(uuid.uuid4()) for _ in chunks]

        self.vector_store.add_documents(
            documents=chunks,
            ids=ids
        )
