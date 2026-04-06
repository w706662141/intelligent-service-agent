from langchain_core.tools import tool
from pydantic import BaseModel, Field
from app.schemas.result import ToolResult, ErrorType
from app.db.database import get_mysql_connection
from sqlalchemy import text


class EmployeeInput(BaseModel):
    """查询员工信息输入参数"""
    employee_id: str = Field(description="员工编号,例如 E001")


@tool(args_schema=EmployeeInput)
def query_employee_info(employee_id: str) -> dict:
    """
    用于查询结构化数据（数据库）。

    适用于：
    - 查询员工信息（姓名、部门、薪资）
    - 查询订单、金额、统计数据
    - 精确字段查询

    不适用于：
    - 制度说明
    - 流程说明
    - FAQ问题
    """

    sql = text("""
    SELECT employee_id,name,department_id,role,hire_date
    FROM employee 
    WHERE
    employee_id= :employee_id
    """)
    with get_mysql_connection() as conn:
        result = conn.execute(sql, {'employee_id': employee_id})

        row = result.mappings().fetchone()

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
        data=dict(row)
    ).to_dict()
