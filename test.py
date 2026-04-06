from app.agent.agent import MultiKBCustomerSupportAgent
from app.core.pipeline import Pipeline

pipeline = Pipeline(role='admin')
res = pipeline.run('帮我查下编号为E001的员工，并计算2000底薪，200奖金，0.2税率的工资')
# res = pipeline.run('报销流程怎么走')

print(res)
from pathlib import Path
import hashlib
import pickle

# from app.agent.retrievers import get_retriever
#
# if __name__ == "__main__":
#     retriever = get_retriever()
#     res = retriever.retrieve("报销流程怎么走")
#     print(res)
#
# agent = MultiKBCustomerSupportAgent()
# res = agent.run("报销流程怎么走")
# print(res)
# compress_docs [Document(metadata={'source': 'hr_policy.txt', 'doc_id': 'hr_policy',
#                                   'doc_hash': 'd6cbacf43b34cccbe95ee5200f495273',
#                                   'chunk_index': 5, 'chunk_id': 'hr_policy_chunk_5',
#                                   'chunk_hash': '7f75cc979e4250488aa9dbf840b4cdba',
#                                   'created_at': '2026-03-09T21:08:27.840866',
#                                   'bm25_score': 1.0, 'vector_score': 0.9904642189091399,
#                                   'hybrid_score': 0.996185687563656},
#                         page_content='员工发生差旅或业务相关费用后，应在出差或业务结束后 7 个工作日内提交报销申请。报销流程包括：填写报销单；上传合法有效的发票照片；经部门负责人审批。')]
