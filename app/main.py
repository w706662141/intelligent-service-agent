import threading
import time

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
load_dotenv(BASE_DIR / ".env")

from fastapi import FastAPI
from app.api.chat import router as chat_router, session_manager

app = FastAPI(title="Multi-KB Customer Support Agent")
app.include_router(chat_router)


def _session_cleanup_loop(interval: int = 300):
    while True:
        time.sleep(interval)
        expired = session_manager.cleanup_expired()
        if expired > 0:
            print(f"[SessionManager] 已清理 {expired} 个过期会话")


cleanup_thread = threading.Thread(target=_session_cleanup_loop, daemon=True)
cleanup_thread.start()
