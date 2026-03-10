from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.schemas.result import ToolResult, ErrorType
from app.db.database import get_connection

FAKE_EMPLOYEE_DB = {
    "E001": {"name": "张三", "department": "HR", "role": "经理"},
    "E002": {"name": "李四", "department": "IT", "role": "工程师"},
}


class EmployeeInput(BaseModel):
    """查询员工信息输入参数"""
    employee_id: str = Field(description="员工编号,例如 E001")


@tool(args_schema=EmployeeInput)
def query_employee_info(employee_id: str) -> dict:
    """员工信息查询"""

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT employee_id,name,department,role FROM employees WHERE employee_id=?",
                       (employee_id,)
                       )

        row = cursor.fetchone()

    if not row:
        return ToolResult(
            success=False,
            error_type=ErrorType.NOT_FOUND,
            message="未找到该员工",
        ).to_dict()

    return ToolResult(
        success=True,
        error_type=ErrorType.NONE,
        message="查询成功",
        data=row
    ).to_dict()
