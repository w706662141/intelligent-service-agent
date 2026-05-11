from app.agent.agent import MultiKBCustomerSupportAgent
from app.agent.executor import ReActPlanExecutor
from app.core.pipeline import Pipeline
import time
# pipeline = Pipeline(role='admin')
# res = pipeline.run('帮我查下编号为E001的员工，并计算2000底薪，200奖金，0.2税率的工资')
# res = pipeline.run('报销流程怎么走')

# print(res)

pipeline = ReActPlanExecutor(role='admin')
# res = pipeline.run('帮我查一下编号为E001的员工,并查询出所有和E001员工相关的订单')
start=time.perf_counter()
res = pipeline.run('帮我查一下编号为E001的员工,并查询出所有和E001员工相关的订单')
# res = pipeline.run('中国首都是哪里？都有哪些好玩的')
end_time = time.perf_counter()
print('res', res)
print('用时：',end_time-start)