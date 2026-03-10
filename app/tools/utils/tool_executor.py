from app.tools.utils.registery import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_call):
        tool_name = tool_call["name"]
        args = tool_call["args"]

        tool = self.registry.get(tool_name)
        return tool.invoke(args)
