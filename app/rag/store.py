from app.config.collection_name_urls import get_collection_path
from app.file_kb.loader import load_or_build_chunks

hr_file_path = get_collection_path('hr_kb')
tech_file_path = get_collection_path('tech_kb')
faq_file_path = get_collection_path('faq_kb')

HR_CHUNKS = None
FAQ_CHUNKS = None
TECH_CHUNKS = None


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
