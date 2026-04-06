from app.file_kb.loader import load_docs
from app.file_kb.splitter import split_docs

from app.vector_store.qdrant_store import QdrantStore


def ingest_file(path):
    print("Loading docs")

    docs = load_docs(path)

    print("splitting docs")

    chunks = split_docs(docs)

    store = QdrantStore()

    doc_id = chunks[0].metadata['doc_id']

    existing = store.get_existing_chunks(doc_id)

    to_add = []

    new_ids = set()

    for chunk in chunks:

        chunk_id = chunk.metadata['chunk_id']

        chunk_hash = chunk.metadata['chunk_hash']

        new_ids.add(chunk_id)

        if chunk_id not in existing:
            to_add.append(chunk)

        elif existing[chunk_id] != chunk_hash:
            to_add.append(chunk)

    to_delete = []

    for old_id in existing.keys():

        if old_id not in new_ids:
            to_delete.append(old_id)

    store.delete_chunks(to_delete)

    store.upsert_chunks(to_add)

    print("新增/更新:", len(to_add))

    print("删除:", len(to_delete))
