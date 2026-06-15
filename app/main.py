import threading
import time

from dotenv import load_dotenv
from pathlib import Path
from contextlib import asynccontextmanager

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
load_dotenv(BASE_DIR / ".env")
from app.api.admin import router as admin_router
from app.api.conversation import router as conversation_router
from app.api.chat import router as chat_router
from fastapi import FastAPI, Depends
import os
from app.api.auth import router as auth_router
IS_PROD = os.getenv('ENV') == "production"


# 账号 admin 密码 admin123

@asynccontextmanager
async def lifespan(app: FastAPI):
    if IS_PROD:
        print("🚀 [生产模式] Lifespan 开始全量按顺序点名预热...")
        # ---- 重资源预加载 ----
        from app.rag.embeddings import get_embeddings  # 神经网络模型 ~1.3GB
        from app.core.reranker import get_reranker_model
        from app.rag.store import (
            get_hr_chunks, get_faq_chunks,
            get_tech_chunks, get_rag_collection_chunks,
        )
        from app.hybrid_score.bm25 import get_bm25_retriever

        print("[Lifespan] 加载 Embedding 模型...")
        get_embeddings()

        print("[Lifespan] 加载 reranker 模型...")
        get_reranker_model()

        print("[Lifespan] 加载文档 Chunks...")
        chunks = get_rag_collection_chunks()  # 其他3个按需加载即可

        print("[Lifespan] 构建 BM25 索引...")
        get_bm25_retriever(chunks, collection_name='rag_docs')

        print("[Lifespan] 所有资源加载完成")

        print("✨ [生产模式] 全量预热完成，线上运行无锁裸跑！")
    else:
        print("💻 [开发模式] 智能客服系统瞬间秒启，等待按需触发...")
    yield


app = FastAPI(lifespan=lifespan, title="Multi-KB Customer Support Agent")
app.include_router(chat_router)
app.include_router(conversation_router)
app.include_router(admin_router)
app.include_router(auth_router)
# def _session_cleanup_loop(interval: int = 300):
#     while True:
#         time.sleep(interval)
#         expired = session_manager.cleanup_expired()
#         if expired > 0:
#             print(f"[SessionManager] 已清理 {expired} 个过期会话")


# cleanup_thread = threading.Thread(target=_session_cleanup_loop, daemon=True)
# cleanup_thread.start()
