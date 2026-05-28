from pathlib import Path

from app.config.collection_name_urls import get_collection_path
from app.file_kb.loader import load_or_build_chunks, load_or_build_chunks_incremental
from threading import Lock

BASE_DIR = Path(__file__).resolve().parent
hr_file_path = get_collection_path('hr_kb')
tech_file_path = get_collection_path('tech_kb')
faq_file_path = get_collection_path('faq_kb')

DATA_PATH = BASE_DIR / "app" / "data"

_CHUNKS = {
    'HR_CHUNKS': None,
    'FAQ_CHUNKS': None,
    'TECH_CHUNKS': None,
    'RAG_COLLECTION_CHUNKS': None,
}

_CHUNKS_LOCK = {chunk: Lock() for chunk in _CHUNKS}

HR_CHUNKS = None
FAQ_CHUNKS = None
TECH_CHUNKS = None
RAG_COLLECTION_CHUNKS = None


def get_hr_chunks():
    if _CHUNKS['HR_CHUNKS'] is None:
        with _CHUNKS_LOCK['HR_CHUNKS']:
            if _CHUNKS['HR_CHUNKS'] is None:
                _CHUNKS['HR_CHUNKS'] = load_or_build_chunks('hr_kb', str(hr_file_path))
    return _CHUNKS['HR_CHUNKS']


def get_faq_chunks():
    if _CHUNKS['FAQ_CHUNKS'] is None:
        with _CHUNKS_LOCK['FAQ_CHUNKS']:
            if _CHUNKS['FAQ_CHUNKS'] is None:
                _CHUNKS['FAQ_CHUNKS'] = load_or_build_chunks('faq_kb', str(faq_file_path))
    return _CHUNKS['FAQ_CHUNKS']


def get_tech_chunks():
    if _CHUNKS['TECH_CHUNKS'] is None:
        with _CHUNKS_LOCK['TECH_CHUNKS']:
            if _CHUNKS['TECH_CHUNKS'] is None:
                _CHUNKS['TECH_CHUNKS'] = load_or_build_chunks('tech_kb', str(tech_file_path))
    return _CHUNKS['TECH_CHUNKS']


def get_rag_collection_chunks():
    if _CHUNKS['RAG_COLLECTION_CHUNKS'] is None:
        with _CHUNKS_LOCK['RAG_COLLECTION_CHUNKS']:
            if _CHUNKS['RAG_COLLECTION_CHUNKS'] is None:
                _CHUNKS['RAG_COLLECTION_CHUNKS'] = load_or_build_chunks_incremental("rag_docs", DATA_PATH)
    return _CHUNKS['RAG_COLLECTION_CHUNKS']
