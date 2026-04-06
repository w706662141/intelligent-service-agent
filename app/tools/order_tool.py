from typing import Optional

from langchain_core.tools import tool
from pydantic import Field, BaseModel
from app.schemas.result import ToolResult, ErrorType
from app.db.database import get_mysql_connection
from sqlalchemy import text


class OrderInput(BaseModel):
    """查询工单输入参数"""
    order_id: str = Field(None, description="工单编号")
    employee_id: Optional[str] = Field(None, description="员工编号，如 E001。用于过滤该员工名下的工单。")


@tool(args_schema=OrderInput)
def query_order(order_id: str = None, employee_id: str = None) -> dict:
    """查询工单状态"""

    if order_id:
        sql = text("""
            SELECT * FROM orders WHERE 
        order_id= :order_id
        """)
        params = {'order_id': order_id}

    elif employee_id:
        sql = text("""
            SELECT * FROM orders WHERE 
        employee_id= :employee_id
        """)
        params = {'employee_id': employee_id}

    else:
        return {"error": "请提供 order_id 或 employee_id"}

    with get_mysql_connection() as conn:
        result = conn.execute(sql, params)

        row = [dict(r) for r in result.mappings().fetchall()]

    if not row:
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
        data=row
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
