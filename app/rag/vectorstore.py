from langchain_chroma import Chroma
from ..rag.embeddings import get_embeddings
from app.config.urls_config import CHROMA_DIR


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


def load_chroma_vectorstore(
        collection_name: str,
        persist_dir: str = str(CHROMA_DIR)
):
    embeddings = get_embeddings()

    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=persist_dir
    )


def get_retriever(collection_name: str):
    """
    从指定 collection 获取 retriever
    """

    embeddings = get_embeddings()

    vectorstore = Chroma(
        persist_directory=str(CHROMA_DIR),
        collection_name=collection_name,
        embedding_function=embeddings
    )
    return vectorstore.as_retriever(search_kwargs={"k": 3})
