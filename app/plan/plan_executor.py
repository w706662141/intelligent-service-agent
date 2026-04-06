from app.plan.plan_schema import Plan


class PlanExecutor:

    def __init__(self, tool_registry):
        self.tool_registry = tool_registry

    def execute(self, plan: Plan):
        results = {}

        for step in plan.steps:
            tool = self.tool_registry.get(step.tool)

            if step.depends_on:
                for dep in step.depends_on:
                    if dep not in results:
                        raise ValueError(f"依赖未完成: step {dep}")
            print(f"执行 Step {step.step_id}: {step.description}")

            result = tool.invoke(**step.args)

            if not result.get('success'):
                print(f"Step {step.step_id} 执行失败")
                break

            results[step.step_id] = result

        return results