import json

from app.core.llm_factory import create_llm
from app.tools.utils.tool_config import EnhancedJSONEncoder
from app.tools.utils.tool_executor import ToolExecutor
from app.tools.utils.registery import create_default_registry
from app.tools.utils.tool_manager import ToolManager
from app.schemas.error import ErrorType
from app.core.llm import get_validator_model
from langchain_core.messages import (AIMessage, HumanMessage, SystemMessage, ToolMessage)


class Pipeline:

    def __init__(self, role):
        self.registry = create_default_registry()
        self.tool_manager = ToolManager(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.llm = create_llm(role, self.tool_manager)
        self.summarize_llm = get_validator_model()
        self.system_content = \
            """你是企业级业务助手。
            - 成功时不要再次调用工具
            - 非可重试错误不要再次调用
            """

    def run(self, question: str, context: dict = None, history: str = None):

        messages = [
            SystemMessage(content=self.system_content)
        ]

        if history:
            messages.append(
                SystemMessage(content=f"以下是历史对话：\n{history}")
            )

        if context:
            context_str = json.dumps(context, ensure_ascii=False, indent=2)
            question = f"""
            任务:
            {question}
            已有信息:
            {context_str}
            """

        messages.append(HumanMessage(content=question))

        max_steps = 3
        called_signatures = set()

        print('message', messages)

        for _ in range(max_steps):

            response: AIMessage = self.llm.invoke(messages)
            print('response', response)
            if not response.tool_calls:
                yield response.content
                return

            messages.append(response)
            tool_results = []
            has_retryable_error = False
            print('tool_call', response.tool_calls)

            for tool_call in response.tool_calls:

                sig = f"{tool_call['name']}_{str(tool_call['args'])}"

                if sig in called_signatures:

                    # return {
                    #     "success": False,
                    #     "error_type": "REPEAT_BLOCKED",
                    #     "message": "多次重复查询未果，任务已终止",
                    #     "data": None
                    # }
                    yield "处理失败，请稍后再试"
                    return
                called_signatures.add(sig)

                result = self.executor.execute(tool_call, messages=messages)

                print('result', result)
                tool_results.append((tool_call, result))

                success = result.get('success')
                error_type = result.get('error_type')

                if not success and error_type not in [
                    ErrorType.RETRYABLE,
                    ErrorType.TIMEOUT
                ]:
                    yield json.dumps(result, ensure_ascii=False)
                    return
                if not success:
                    has_retryable_error = True

            is_rag_only = (len(tool_results) == 1 and tool_results[0][0]['name'] == 'rag_search')

            if is_rag_only:
                rag_result = tool_results[0][1]
                print('rag_result', rag_result)
                if rag_result.get('success'):
                    data = rag_result.get('data')
                    if isinstance(data, list):
                        data = '\n'.join(data)

                    messages.append(
                        ToolMessage(
                            content=json.dumps(data, ensure_ascii=False),
                            tool_call_id=tool_results[0][0]['id']
                        )
                    )

                    # ★★★ 这里是关键：invoke → stream ★★★
                    for chunk in self.summarize_llm.stream(messages):
                        yield chunk.content
                    return
                    # return data.get('answer')

            if has_retryable_error:
                for tool_call, result in tool_results:
                    messages.append(
                        ToolMessage(
                            content=json.dumps(result, ensure_ascii=False),
                            tool_call_id=tool_call['id']
                        )
                    )
                continue

            for tool_call, result in tool_results:
                messages.append(
                    ToolMessage(
                        content=json.dumps(result, ensure_ascii=False, cls=EnhancedJSONEncoder),
                        tool_call_id=tool_call['id']
                    )
                )
            # ★★★ 这里是关键：invoke → stream ★★★
            for chunk in self.summarize_llm.stream(messages):
                yield chunk.content
            return

            # final_response = self.summarize_llm.invoke(messages)

            # return final_response.content

        # return {
        #     "success": False,
        #     "error_type": "MAX_STEPS_EXCEEDED",
        #     "message": "处理失败，请稍后再试",
        #     "data": None
        # }
        yield "处理失败，请稍后再试"
