from pathlib import Path

from app.file_kb.loader import load_docs
from app.file_kb.splitter import split_docs
from app.rag.vectorstore import build_chroma_vectorstore
from app.rag.store import HR_CHUNKS

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "hr_policy.txt"

docs = load_docs(str(DATA_PATH))
chunks = split_docs(docs)

HR_CHUNKS.clear()
HR_CHUNKS.extend(chunks)

build_chroma_vectorstore(
    docs=chunks,
    collection_name="hr_kb"
)

print("HR 知识库构建完成")
