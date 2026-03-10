import sys
from datetime import datetime
import json
import logging

logger = logging.getLogger('rag')
logger.setLevel(logging.INFO)

# ⭐ 关键：加 handler（只加一次）
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[RAG] %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def log_event(request_id: str, stage: str, **kwargs):
    log = {
        "request_id": request_id,
        "stage": stage,
        "timestamp": datetime.now().isoformat(),
        **kwargs
    }
    logger.info(json.dumps(log, ensure_ascii=False))
