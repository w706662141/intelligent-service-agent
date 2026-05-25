from langchain_huggingface import HuggingFaceEmbeddings

_embeeding = None

def get_embeddings():
    global _embeeding
    if not _embeeding:
        _embeeding = HuggingFaceEmbeddings(
            # model_name="BAAI/bge-m3",
            model_name="BAAI/bge-large-zh",
            encode_kwargs={"normalize_embeddings": True}
        )

    return _embeeding
