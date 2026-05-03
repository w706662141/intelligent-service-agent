from app.agent.agent import MultiKBCustomerSupportAgent
from app.agent.executor import ReActPlanExecutor
from app.core.pipeline import Pipeline

# pipeline = Pipeline(role='admin')
# res = pipeline.run('帮我查下编号为E001的员工，并计算2000底薪，200奖金，0.2税率的工资')
# res = pipeline.run('报销流程怎么走')

# print(res)

pipeline = ReActPlanExecutor(role='admin')
# res = pipeline.run('帮我查一下编号为E001的员工,并查询出所有和E001员工相关的订单')
res = pipeline.run('电子商务的概念是什么？')
print('res', res)