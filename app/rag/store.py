from pathlib import Path

from app.config.collection_name_urls import get_collection_path
from app.file_kb.loader import load_or_build_chunks,load_or_build_chunks_incremental

BASE_DIR = Path(__file__).resolve().parent
hr_file_path = get_collection_path('hr_kb')
tech_file_path = get_collection_path('tech_kb')
faq_file_path = get_collection_path('faq_kb')

DATA_PATH = BASE_DIR / "app" / "data"

HR_CHUNKS = None
FAQ_CHUNKS = None
TECH_CHUNKS = None
RAG_COLLECTION_CHUNKS = None


def get_hr_chunks():
    global HR_CHUNKS
    if HR_CHUNKS is None:
        HR_CHUNKS = load_or_build_chunks('hr_kb', str(hr_file_path))
    return HR_CHUNKS


def get_faq_chunks():
    global FAQ_CHUNKS
    if FAQ_CHUNKS is None:
        FAQ_CHUNKS = load_or_build_chunks('faq_kb', str(faq_file_path))
    return FAQ_CHUNKS


def get_tech_chunks():
    global TECH_CHUNKS
    if TECH_CHUNKS is None:
        TECH_CHUNKS = load_or_build_chunks('tech_kb', str(tech_file_path))
    return TECH_CHUNKS


def get_rag_collection_chunks():
    global RAG_COLLECTION_CHUNKS
    if RAG_COLLECTION_CHUNKS is None:
        RAG_COLLECTION_CHUNKS = load_or_build_chunks_incremental("rag_docs", DATA_PATH)

    return RAG_COLLECTION_CHUNKS
