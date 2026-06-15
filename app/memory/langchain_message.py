from langchain_core.messages import AIMessage, HumanMessage


def build_langchain_message(
        history
):
    messages = []

    for item in history:

        if item['role'] == 'user':
            messages.append(
                HumanMessage(content=item['content'])
            )
        else:
            messages.append(
                AIMessage(content=item['content'])
            )

    return messages
