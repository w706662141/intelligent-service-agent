from app.tools.utils.registery import ToolRegistry
import inspect


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(self, tool_call, messages=None):
        tool_name = tool_call["name"]
        args = tool_call["args"]

        tool = self.registry.get(tool_name)

        # if "messages" in tool_demo.invoke.__code__.co_varnames:
        if "messages" in inspect.signature(tool.invoke).parameters:
            args['messages'] = messages

        return tool.invoke(args)
