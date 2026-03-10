# from app.agent.agent import MultiKBCustomerSupportAgent
#
#
# testmodel = MultiKBCustomerSupportAgent()
#
# while True:
#
#
#     query=input("请输入问题")
#     # 手动判断关键词退出
#     if query.lower() in ['q', 'quit', 'exit', '退出']:
#         print("程序已安全退出。")
#         break  # 跳出循环
#     res = testmodel.run(query)
#     print(res)

from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
print(BASE_DIR)
load_dotenv(BASE_DIR / ".env")  # ⭐ 一定要在最上面
from fastapi import FastAPI
from app.api.chat import router as chat_router

app = FastAPI(title="Multi-KB Customer Support Agent")
app.include_router(chat_router)
