import json
from app.prompts.plan_prompt import PLANNER_PROMPT

from app.plan.plan_schema import Plan


class Planner:

    def __init__(self, llm, tools):
        self.llm = llm
        self.tools = tools

    def get_tool_desc(self):
        desc = []
        for tool in self.tools:
            desc.append(f"{tool.name}:{tool.description}")
        return "\n".join(desc)

    def plan(self, question: str) -> Plan:
        prompt = PLANNER_PROMPT.format_messages(
            tool_desc=self.get_tool_desc(),
            question=question
        )

        response = self.llm.invoke(prompt)
        print('plan_response', response)
        try:
            steps_data = json.loads(response.content)
            return Plan(steps=steps_data)
        except Exception as e:
            raise ValueError(f"Plan解析失败: {e}")
