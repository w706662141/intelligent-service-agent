import json

from app.core.llm_factory import create_llm
from app.tools.utils.tool_executor import ToolExecutor
from app.tools.utils.registery import create_default_registry
from app.tools.utils.tool_manager import ToolManager
from app.schemas.error import ErrorType


class Pipeline:

    def __init__(self, role):
        self.registry = create_default_registry()
        self.tool_manager = ToolManager(self.registry)
        self.executor = ToolExecutor(self.registry)
        self.llm = create_llm(role, self.tool_manager)

        self.system_content = \
            """你是企业级业务助手。
            - 成功时不要再次调用工具
            - 非可重试错误不要再次调用
            """

    def run(self, question: str):
        messages = [
            {
                "role": "system",
                "content": self.system_content
            },
            {
                "role": "user",
                "content": question
            }
        ]

        max_steps = 3
        called_signatures = set()

        for _ in range(max_steps):

            response = self.llm.invoke(messages)

            if not response.tool_calls:
                return response.content

            messages.append(response)

            tool_results = []
            has_retryable_error = False
            print(response.tool_calls)
            for tool_call in response.tool_calls:

                sig = f"{tool_call['name']}_{str(tool_call['args'])}"

                if sig in called_signatures:
                    return {
                        "success": False,
                        "error_type": "REPEAT_BLOCKED",
                        "message": "多次重复查询未果，任务已终止",
                        "data": None
                    }
                called_signatures.add(sig)

                result = self.executor.execute(tool_call)
                tool_results.append((tool_call, result))

                success = result.get('success')
                error_type = result.get('error_type')

                if not success and error_type not in [
                    ErrorType.RETRYABLE,
                    ErrorType.TIMEOUT
                ]:
                    return result

                if not success:
                    has_retryable_error = True

            if has_retryable_error:
                for tool_call, result in tool_results:
                    messages.append({
                        "role": "tool",
                        "content": json.dumps(result, ensure_ascii=False),
                        "tool_call_id": tool_call["id"]
                    })
                continue

            for tool_call, result in tool_results:
                messages.append({
                    "role": "tool",
                    "content": json.dumps(result, ensure_ascii=False),
                    "tool_call_id": tool_call["id"]
                })

            final_response = self.llm.invoke(messages)

            return final_response.content

        return {
            "success": False,
            "error_type": "MAX_STEPS_EXCEEDED",
            "message": "处理失败，请稍后再试",
            "data": None
        }
