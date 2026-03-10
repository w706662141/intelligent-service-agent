from langchain_core.runnables import RunnableLambda
from app.prompts.extract_prompt import extract_prompt
from app.core.llm import get_model
from langchain_core.documents import Document

llm = get_model()


def _msg_to_text(msg):
    return msg.content if hasattr(msg, "content") else str(msg)


llm_chain_extractor = (
        extract_prompt
        | llm
        | RunnableLambda(_msg_to_text)

)


def compress_document(doc, query, min_tokens=300):
    if len(doc.page_content) <= min_tokens:
        return doc

    compressed = llm_chain_extractor.invoke({
        "query": query,
        "document": doc.page_content
    }).strip()

    # LLM 返回空，兜底
    if not compressed:
        return doc
    return [Document(page_content=compressed,
                     metadata=doc.metadata)]
