import os
import pickle
from pathlib import Path
from typing import List
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from app.file_kb.splitter import split_docs
from app.file_kb.utils import file_md5

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


def _load_single_doc(file_path):
    """
    加载文档，并添加基础 metadata
    """
    docs = TextLoader(file_path, encoding='utf-8').load()

    file_name = os.path.basename(file_path)
    doc_id = os.path.splitext(file_name)[0]
    doc_hash = file_md5(file_path)

    for doc in docs:
        doc.metadata['source'] = file_name
        doc.metadata['doc_id'] = doc_id
        doc.metadata['doc_hash'] = doc_hash

    return docs


def load_docs(path):
    """
    加载文档，并添加基础 metadata
    支持：
    - 单文件
    - 目录（自动遍历）
    """

    path = Path(path)

    all_docs = []

    if path.is_file():
        return _load_single_doc(path)

    elif path.is_dir():
        for file in path.glob("**/*"):
            if file.is_file() and file.suffix in [".txt", '.md']:
                docs = _load_single_doc(file)
                all_docs.extend(docs)
        return all_docs
    else:
        raise ValueError(f"路径不存在{path}")


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


def scan_files(path):
    path = Path(path)

    files = []

    for f in path.glob("**/*"):
        if f.is_file() and f.suffix in ['.txt', '.md']:
            files.append(f)
    return files


def load_cache(cache_path):
    if not cache_path.exists():
        return {"docs": {}}

    with open(cache_path, 'rb') as f:
        return pickle.load(f)


def load_or_build_chunks_incremental(collection_name: str, dir_path: str):
    cache_path = _get_cache_path(collection_name)
    cache_data = load_cache(cache_path)

    old_docs = cache_data.get('docs', {})

    new_docs_cache = {}

    all_chunks = []

    files = scan_files(dir_path)

    for file in files:
        file_path = str(file)
        file_name = file.stem

        current_hash = file_md5(file_path)

        # ✅ 情况1：文件没变 → 直接复用
        if file_name in old_docs:
            if old_docs[file_name]['doc_hash'] == current_hash:
                print(f"[KB] ♻️ 复用: {file_name}")

                chunks = old_docs[file_name]['chunks']
                new_docs_cache[file_name] = old_docs[file_name]

                all_chunks.extend(chunks)
                continue

        # ✅ 情况2：新增 or 修改 → 重建
        print(f"[KB] 更新:{file_name}")

        docs = _load_single_doc(file)
        chunks = split_docs(docs)

        new_docs_cache[file_name] = {
            'doc_hash': current_hash,
            "chunks": chunks
        }

        all_chunks.extend(chunks)

    with open(cache_path, 'wb') as f:
        pickle.dump({
            'docs': new_docs_cache
        }, f)

    return all_chunks
