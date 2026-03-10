import os
import pickle
from pathlib import Path
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from app.file_kb.splitter import split_docs
from app.file_kb.utils import md5, file_md5

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "file_kb" / 'cache'

CACHE_DIR = Path(DATA_PATH)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _get_cache_path(collection_name: str) -> Path:
    return CACHE_DIR / f"{collection_name}.pkl"


def _get_file_mtime(file_path: str) -> float:
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"[KB INIT ERROR] 知识库文件不存在: {file_path}"
        )
    return os.path.getmtime(file_path)


def _load_chunks(cache_path: Path):
    with open(cache_path, 'rb') as f:
        return pickle.load(f)


def load_docs(path):
    """
    加载文档，并添加基础 metadata
    """
    docs = TextLoader(path, encoding='utf-8').load()

    file_name = os.path.basename(path)
    doc_id = os.path.splitext(file_name)[0]

    doc_hash = file_md5(path)

    for doc in docs:
        doc.metadata['source'] = file_name
        doc.metadata['doc_id'] = doc_id
        doc.metadata['doc_hash'] = doc_hash

    return docs


def _save_chunks(cache_path, chunks, current_file_mtime):
    with open(cache_path, 'wb') as f:
        pickle.dump({
            'chunks': chunks,
            'file_mtime': current_file_mtime
        }, f)


def load_or_build_chunks(collection_name: str, file_path: str) -> List[Document]:
    """
    统一入口：
    - 若缓存存在且文件未更新 → 直接加载
    - 若缓存不存在或文件更新 → 重建
    """

    cache_path = _get_cache_path(collection_name)
    current_file_mtime = _get_file_mtime(file_path)

    # 情况1：缓存存在
    if cache_path.exists():
        data = _load_chunks(cache_path)

        if data['file_mtime'] == current_file_mtime:
            print(f"[KB] ✅ 加载缓存: {collection_name}")
            return data["chunks"]

    # 情况2：缓存不存在或失效
    print(f"[KB] 🔨 构建 chunks: {collection_name}")

    docs = load_docs(file_path)
    chunks = split_docs(docs)

    _save_chunks(cache_path, chunks, current_file_mtime)

    return chunks
