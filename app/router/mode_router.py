from langchain.messages import HumanMessage
from app.core.llm_factory import router_llm
from app.prompts.mode_router_prompt import router_prompt


class Router:

    def __init__(self, tool_manager):
        self.llm = router_llm()
        self.tool_manager = tool_manager

    def route(self, role: str, question: str, history=None):
        tools = self.tool_manager.get_tools_by_role(role)

        tool_desc = '\n'.join([
            f"-{tool.name}:{tool.description}"
            for tool in tools
        ])
        history_str = history if history else "无"

        prompt = router_prompt.format_messages(question=question,
                                               tool_desc=tool_desc,
                                               history=history_str
                                               )

        resp = self.llm.invoke(prompt)

        result = resp.content.strip().upper()

        if result not in ["SIMPLE", "TOOL", "COMPLEX"]:
            return 'SIMPLE'

        return result
