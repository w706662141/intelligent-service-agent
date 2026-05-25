from app.agent.executor import ReActPlanExecutor


for chunk in ReActPlanExecutor('admin').run('请假流程是什么样的'):
    print(chunk,end='',flush=True)
print()
