from app.prompts.classifier_prompt import classifier_prompt

CATEGORIES = ['FAQ', 'HR', 'TECH', 'CHAT']


def classify_question(question: str, llm) -> str:
    """
     将用户问题分类到具体知识域
    """

    resp = llm.invoke(
        classifier_prompt.format_messages(question=question)
    ).content.strip().upper()

    return resp if resp in CATEGORIES else "CHAT"
