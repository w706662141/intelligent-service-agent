from app.core.llm import get_validator_model
from langchain_core.prompts import ChatPromptTemplate


def create_llm(role, tool_manager):
    base_model = get_validator_model()
    tools = tool_manager.get_tools_by_role(role)

    return base_model.bind_tools(tools)


def summarize_llm():
    base_model = get_validator_model()

    prompt = ChatPromptTemplate.from_messages([])

    chain = prompt | base_model

    return chain
