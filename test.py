# from app.core.pipeline import Pipeline
#
# p = Pipeline("admin")
# res = p.run("帮我查询E001员工信息，同时帮我查询1001工单信息")
# print(res)
from qdrant_client import QdrantClient
from qdrant_client.http import models
from app.rag.embeddings import get_embeddings
# 连接到 Docker 容器
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore

client = QdrantClient(url="http://127.0.0.1:6333")

vector_store = QdrantVectorStore(
    client=client,
    collection_name='rag_docs',
    embedding=get_embeddings()
)

retriever = vector_store.as_retriever(
    search_kwargs={"k": 3})

docs=retriever.invoke('员工假期多少天')

for d in docs:
    print(d.page_content)