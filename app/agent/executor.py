import json
from typing import List, Dict

from app.core.llm import get_validator_model, get_model
from app.tools.utils.registery import create_default_registry
from app.tools.utils.tool_executor import ToolExecutor
from app.core.pipeline import Pipeline
from app.tools.utils.tool_manager import ToolManager
from app.memory.short_memory import ShortTermMemory
from app.plan.plan_executor import PlanExecutor
from app.plan.planner import Planner
from app.router.mode_router import Router
from app.content.context_builder import format_history_for_llm
from app.config.agent_log import log_event
from dataclasses import dataclass


@dataclass
class ExecutionContext:
    """执行上下文 - Executor 需要的运行时信息"""
    session_id: str
    role: str
    history: List[Dict[str, str]]
    max_turns: int = 20


class ReActPlanExecutor:

    def __init__(self, role):
        self.registry = create_default_registry()
        self.tool_manager = ToolManager(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.llm = get_model()
        self.summarize_llm = get_validator_model()
        self.pipeline = Pipeline(role)
        # self.memory = ShortTermMemory()
        self.plan_executor = PlanExecutor(self.registry, self.executor, self.llm)
        self.planner = Planner(self.llm, self.tool_manager.get_tools_by_role(role))
        self.router = Router(self.tool_manager)
        self.role = role
        self.summarize_llm = get_validator_model()

    def rewrite(self, question, history):

        # history = format_history_for_llm(self.memory.get())

        prompt = f"""
        
        历史对话:
        {history}

        当前问题:
        {question}

        任务：请补全指代，使问题清晰完整。
        要求：
        1. 如果问题本身完整，请直接原样返回。
        2. 只输出重写后的问题文字，不要包含任何解释、标点前缀或分析。
        3. 解析代词（他/她/它/这个/那个）"
        4. 补全缺失主体"
        5. 不改变原意，把口语化的表达变得规范"
        6. 只输出改写后的问题"
        7. **名词化与流程化**：将动词短语转为名词短语（如：'怎么报销' -> '报销流程'）"
        8. **去口语化**：移除‘我’、‘怎么’、‘咋办’、‘请问’等修饰词及标点符号"
        9. **保持原意**：严禁引入原问题中不存在的业务实体。"
        10 . **极致简洁**：只输出改写后的文本，严禁任何解释或前导词。"
        """

        return self.llm.invoke(prompt).content

    # def simple_run(self, question):
    #     return self.llm.invoke(question).content
    #
    # def react_run(self, question):
    #     history = format_history_for_llm(self.memory.get())
    #     return self.pipeline.run(question, history=history)
    #
    # def plan_run(self, question):
    #     history = format_history_for_llm(self.memory.get())
    #     plan = self.planner.plan(question)
    #     result = self.plan_executor.execute(plan, history)
    #
    #     prompt = f"""
    #     用户问题:
    #     {question}
    #
    #     执行结果(JSON):
    #     {json.dumps(result["results"], ensure_ascii=False, default=str, indent=2)}
    #
    #     请给出最终答案
    #     """
    #
    #     if not result.get("success"):
    #         return f"执行失败: {result}"
    #     # 3️⃣ 汇总结果（可选）
    #
    #     final_answer = self.summarize_llm.invoke(prompt)
    #
    #     return final_answer

    def _stream_react_run(self, question, history):
        full_answer = ""
        for chunk in self.pipeline.run(question, history=history):
            full_answer += chunk
            yield chunk
        # self.memory.add(self.role, full_answer)

    def _stream_plan_run(self, question, history):
        plan = self.planner.plan(question)
        result = self.plan_executor.execute(plan, history)
        prompt = f"""
        用户问题: {question}
        执行结果(JSON): {json.dumps(result["results"], ensure_ascii=False, default=str, indent=2)}
        请给出最终答案
        """
        full_answer = ""
        for chunk in self.summarize_llm.stream(prompt):
            text = chunk.content
            full_answer += text
            yield text
        # self.memory.add(self.role, self.normalize_output(full_answer))

    def normalize_output(self, res):
        if hasattr(res, 'content'):
            res = res.content
        if '最终答案' in res:
            res = res.replace('最终答案', '').strip()
        return res

    def run(self, question: str, context: ExecutionContext):

        history = format_history_for_llm(context.history)
        print('question', question)
        question = self.rewrite(question, history)
        print('rewrite_question', question)
        # history = format_history_for_llm(self.memory.get())

        router_res = self.router.route(self.role, question, history)
        log_event(
            request_id='11111111',
            stage='run',
            router_res=router_res
        )
        if router_res == 'SIMPLE':
            full_answer = ""
            log_event(
                router='SIMPLE'
            )
            for chunk in self.llm.stream(question):
                full_answer += chunk.content
                yield chunk.content
            # self.memory.add(self.role, full_answer)
            # result = self.simple_run(question)
        elif router_res == 'TOOL':
            log_event(
                router='TOOL'
            )
            yield from self._stream_react_run(question, history)
            # result = self.react_run(question)
        else:
            log_event(
                router='COMPLEX'
            )
            yield from self._stream_plan_run(question, history)
            # result = self.plan_run(question)

        # self.memory.add(self.role, result)

        # result = self.normalize_output(result)

        # return result
