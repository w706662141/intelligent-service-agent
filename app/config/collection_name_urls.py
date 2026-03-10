from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"

COLLECTION_REGISTRY = {
    'hr_kb': {
        'path': DATA_PATH / 'hr_policy.txt',
    },
    'faq_kb': {
        'path': DATA_PATH / 'faq.txt'
    },
    'tech_kb': {
        'path': DATA_PATH / 'tech_support.txt'
    }

}


def get_collection_path(collection_name: str) -> Path:
    cfg = COLLECTION_REGISTRY.get(collection_name)
    if not cfg:
        raise ValueError(f"Unknown collection_name: {collection_name}")
    return cfg["path"]
