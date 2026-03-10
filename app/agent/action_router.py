import json
import os

from langchain_groq import ChatGroq

from app.agent.schema import ToolCall

from app.prompts.task.router import ACTION_ROUTER_PROMPT


class ActionRouter:

    def __init__(self, llm_instance=None):
        if llm_instance:
            self.llm = llm_instance
        else:
            self.llm = ChatGroq(
                api_key=os.getenv('GROQ_API_KEY'),
                model_name="llama-3.3-70b-versatile",
                temperature=0,
                max_retries=2,
            )

    def route(self, question: str) -> ToolCall | None:
        prompt = ACTION_ROUTER_PROMPT.format(question=question)
        response = self.llm.invoke(prompt).content.strip()
        print('response', response)
        if response.lower() == "null":
            return None

        try:
            data = json.loads(response)
            print('data', data)
            return ToolCall(**data)
        except Exception:
            return None
