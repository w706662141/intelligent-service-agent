from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.router.intent_schema import COLLECTION_INTENTS


class IntentRouter:

    def __init__(self, llm):
        self.llm = llm
        self.parser = StrOutputParser()
        self.prompt = ChatPromptTemplate.from_template("""
       你是一个企业级智能客服系统的意图分类器。

        可选知识库：
        {collections}
        
        用户问题：
        {question}
        
        请只返回最合适的 collection_name（不要解释）：
       """)

    def route(self, question: str) -> str:
        # 1️⃣ 把 collection 的“语义定义”整理成 prompt 文本
        collection_desc = '\n'.join(
            [f"-{k}:{v['desc']}" for k, v in COLLECTION_INTENTS.items()]
        )
        # 2️⃣ prompt → LLM → 纯字符串输出
        chain = self.prompt | self.llm | self.parser

        result = chain.invoke({
            "collections": collection_desc,
            "question": question
        })

        result = result.strip()

        # 3️⃣ 安全兜底（非常重要）
        if result not in COLLECTION_INTENTS:
            return "faq_kb"

        return result
