import os
from pathlib import Path
from app.vector_store.ingest_pipeline import ingest_file

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data"


def ingest_all():
    for file in os.listdir(DATA_PATH):
        path = os.path.join(DATA_PATH, file)
        print("Processing:", file)

        ingest_file(path)


if __name__ == '__main__':
    ingest_all()
