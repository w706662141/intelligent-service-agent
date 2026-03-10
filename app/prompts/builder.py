from app.prompts.rag.rag_template import RAG_PROMPT_TEMPLATE


def build_rag_prompt(system_prompt, task_prompt, history, docs, question):
    return RAG_PROMPT_TEMPLATE.format_messages(
        system_prompt=system_prompt,
        task_prompt=task_prompt,
        history=history,
        context=docs,
        question=question
    )
