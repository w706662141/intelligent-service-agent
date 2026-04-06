class ToolManager:

    def __init__(self, registry):
        self.registry = registry

        self.role_mapping = {
            "employee": ["query_order", 'query_employee_info', 'rag_search'],
            "finance": ["calculate_salary", 'rag_search'],
            "admin": self.registry.list_names()
        }

    def get_tools_by_role(self, role):
        tool_names = self.role_mapping.get(role, [])
        return [
            self.registry.get(name)
            for name in tool_names
        ]
