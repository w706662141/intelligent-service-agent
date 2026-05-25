from langchain_chroma import Chroma
from ..rag.embeddings import get_embeddings
from app.config.urls_config import CHROMA_DIR
from app.vector_store.qdrant_client import get_client
from langchain_qdrant import QdrantVectorStore


def build_chroma_vectorstore(
        docs,
        collection_name: str,
        persist_dir: str = str(CHROMA_DIR)
):
    embeddings = get_embeddings()

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name=collection_name,
        persist_directory=persist_dir
    )
    return vectorstore


def build_qdrant_vectorstore():
    pass



def load_qdrant_vectorstore(
        collection_name: str,
):
    embeddings = get_embeddings()
    client = get_client()

    return QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )
