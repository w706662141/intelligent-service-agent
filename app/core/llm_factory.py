from app.core.llm import get_validator_model


def create_llm(role, tool_manager):
    base_model = get_validator_model()
    tools = tool_manager.get_tools_by_role(role)

    return base_model.bind_tools(tools)
