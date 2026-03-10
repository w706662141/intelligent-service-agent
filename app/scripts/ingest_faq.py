from app.file_kb.loader import load_docs
from app.file_kb.splitter import split_docs
from app.rag.vectorstore import build_chroma_vectorstore
from pathlib import Path
from app.rag.store import FAQ_CHUNKS
BASE_DIR = Path(__file__).resolve().parent.parent

DATA_PATH = BASE_DIR / "data" / 'faq.txt'

docs = load_docs(str(DATA_PATH))
chunks = split_docs(docs)

FAQ_CHUNKS.clear()
FAQ_CHUNKS.extend(chunks)

build_chroma_vectorstore(
    docs=chunks,
    collection_name='faq_kb'
)

print("知识库构建完成")
