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
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.vector_store.load_chunks import QdrantChunkLoader

client = QdrantClient(url="http://127.0.0.1:6333")


# res=client.scroll(
#     collection_name='rag_docs',
#     limit=1
# )
# ([Record(id='0046879a-ec92-47c2-bcf2-daed741ebce7',
# payload={'page_content': 'Q: 请假流程是怎样的？\nA:公司请假流程如下：\n员工登录内部系统提交请假申请；\n选择请假类型（事假、病假、年假等）；\n填写请假时间及原因；\n提交后由直属主管进行审批；',
# 'metadata': {'source': 'hr_policy.txt', 'doc_id': 'hr_policy',
# 'doc_hash': 'd6cbacf43b34cccbe95ee5200f495273',
# 'chunk_index': 1, 'chunk_id': 'hr_policy_chunk_1',
# 'chunk_hash': 'c614af19e7d96ed88da38164a7cc0c60',
# 'created_at': '2026-03-09T21:08:27.840866'}},
# vector=None, shard_key=None, order_value=None)],
# '0c00182e-a254-48b7-8e72-5380970d4ad3')

# vector_store = QdrantVectorStore(
#     client=client,
#     collection_name='rag_docs',
#     embedding=get_embeddings()
# )

loader = QdrantChunkLoader(
    client=client,
    collection_name='rag_docs',
    text_field='page_content'
)
chunks = loader.load_chunks()

print(chunks)