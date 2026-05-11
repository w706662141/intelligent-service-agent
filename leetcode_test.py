from app.core.llm import get_xiaomi_model

model=get_xiaomi_model()
res=model.invoke('你好')

print(res)