from langchain_core.prompts import ChatPromptTemplate

RAG_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages([
    ('system', "{system_prompt}"),
    ("system", "{task_prompt}"),
    ("system", """
    【对话上下文（仅用于理解问题背景，不作为回答依据）】
    {history}
    """),
    ("system", """
    【已知信息（唯一可作为回答依据）】
    {context}
    """),
    ("human", "{question}")
])
