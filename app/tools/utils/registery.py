from app.tools.employee_tool import query_employee_info
from app.tools.salary_tool import calculate_salary
from app.tools.ticket_tool import query_ticket


class ToolRegistry:

    def __init__(self):
        self._tools = {}

    def register(self, tool):
        self._tools[tool.name] = tool

    def get(self, name):
        return self._tools.get(name)

    def list_all(self):
        return list(self._tools.values())

    def list_names(self):
        return list(self._tools.keys())


def create_default_registry():
    registry = ToolRegistry()
    registry.register(query_ticket)
    registry.register(calculate_salary)
    registry.register(query_employee_info)

    return registry
