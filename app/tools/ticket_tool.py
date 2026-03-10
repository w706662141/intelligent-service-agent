from langchain_core.tools import tool
from pydantic import Field, BaseModel
from app.schemas.result import ToolResult, ErrorType


class TicketInput(BaseModel):
    """查询工单输入参数"""
    ticket_id: str = Field(description="工单编号")


FAKE_DB = {
    "1001": {"status": "处理中", "owner": "HR部门"},
    "1002": {"status": "已完成", "owner": "IT部门"},
}


@tool(args_schema=TicketInput)
def query_ticket(ticket_id: str) -> dict:
    """查询工单状态"""

    ticket = FAKE_DB.get(ticket_id)
    if not ticket:
        return ToolResult(
            success=False,
            message="未找到该工单",
            error_type=ErrorType.NONE,
            data=None,
        ).to_dict()
    return ToolResult(
        success=True,
        error_type=ErrorType.NONE,
        message="查询成功",
        data=ticket
    ).to_dict()

# class TicketQueryTool(BaseTool):
#     name = "query_ticket"
#     description = "查询工单状态"
#     input_model = TicketInput
#
#     def run(self, input_data: TicketInput) -> ToolOutput:
#         ticket = FAKE_DB.get(input_data.ticket_id)
#
#         if not ticket:
#             return ToolOutput(
#                 success=False,
#                 message="未找到该工单",
#                 data=None
#             )
#
#         return ToolOutput(
#             success=True,
#             message="查询成功",
#             data=ticket
#         )
