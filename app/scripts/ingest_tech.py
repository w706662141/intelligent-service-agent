from pathlib import Path

from app.file_kb.loader import load_docs
from app.file_kb.splitter import split_docs
from app.rag.vectorstore import build_chroma_vectorstore
from app.rag.store import TECH_CHUNKS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "tech_support.txt"

docs = load_docs(str(DATA_PATH))
chunks = split_docs(docs)

TECH_CHUNKS.clear()
TECH_CHUNKS.extend(chunks)

build_chroma_vectorstore(
    chunks,
    collection_name="tech_kb"
)

print("TECH 知识库构建完成")
