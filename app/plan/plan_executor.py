from app.plan.plan_schema import Plan
from langchain.messages import HumanMessage
from app.core.pipeline import Pipeline
from app.config.agent_log import log_event


class PlanExecutor:

    def __init__(self, tool_registry, tool_executor, llm):
        self.tool_registry = tool_registry
        self.tool_executor = tool_executor
        self.llm = llm
        self.pipeline = Pipeline('admin')

    def execute(self, plan: Plan, history=None):
        results = {}
        context = {}

        log_event(
            request_id='22222222',
            stage='complex_execute',
            plan=[step.to_dict() for step in plan.steps]
        )

        for step in plan.steps:
            # tool_demo = self.tool_registry.get(step.tool_demo)

            print(f"🚀 执行 Step {step.step_id}: {step.description}")

            if step.depends_on:
                for dep in step.depends_on:
                    if dep not in results:
                        raise ValueError(f"依赖未完成: step {dep}")

                    # 👉 注入依赖结果（核心升级）
                    context[f"step_{dep}"] = results[dep].get('data')

            # =========================
            # 2️⃣ 构造最终参数（🔥关键）
            # =========================
            final_args = {
                **step.args,
                'context': context
            }

            print(f"执行 Step {step.step_id}: {step.description}")

            # =========================
            # 3️⃣ 执行方式分流
            # =========================
            if step.type == 'llm':
                response = self.llm.invoke([
                    HumanMessage(content=f"""
                    任务步骤:{step.description}
                    上下文:{context}
                    """)
                ])

                result = {
                    "success": True,
                    "data": response.content
                }
            elif step.type == 'tool':
                # 👉 统一走 ToolExecutor（不要直接invoke）

                tool_call = {
                    'name': step.tool,
                    'args': final_args,
                    'id': f"step_{step.step_id}"
                }

                result = self.tool_executor.execute(tool_call)
            else:
                result = self.pipeline.run(
                    question=step.description,
                    context=context,
                    history=history
                )
                result = {
                    "success": True,
                    "data": result
                }

            log_event(
                request_id='plan 11111111111',
                stage='plan print',
                plan_result=result
            )

            if not result.get('success'):
                print(f"Step {step.step_id} 执行失败")
                return {
                    "success": False,
                    "failed_step": step.step_id,
                    "error": result
                }

            results[step.step_id] = result

        return {
            "success": True,
            "results": results
        }
