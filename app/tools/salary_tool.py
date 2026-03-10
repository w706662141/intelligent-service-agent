from langchain_core.tools import tool
from app.schemas.result import ToolResult, ErrorType
from pydantic import BaseModel, Field


class SalaryInput(BaseModel):
    """工资计算输入参数"""
    base: float = Field(description="基础工资")
    bonus: float = Field(description="奖金")
    tax_rate: float = Field(description="税率，例如 0.2 表示 20%")


@tool(args_schema=SalaryInput)
def calculate_salary(base: float, bonus: float, tax_rate: float) -> dict:
    """计算税后工资"""

    gross = base + bonus
    tax = gross * tax_rate
    net = gross - tax

    return ToolResult(
        success=True,
        error_type=ErrorType.NONE,
        message='计算完成',
        data={
            "gross": gross,
            "tax": tax,
            "net": net
        }
    ).to_dict()

# class SalaryCalculatorTool(BaseTool):
#     name = "caclculate_salary"
#     description = "计算税后工资"
#     input_model = SalaryInput
#
#     def run(self,input_data:SalaryInput) ->ToolOutput:
#         gross=input_data.base+input_data.bonus
#         tax=gross*input_data.tax_rate
#         net=gross-tax
#
#         return ToolOutput(
#             success=True,
#             message="计算完成",
#             data={
#                 "gross":gross,
#                 "tax":tax,
#                 "net":net
#             }
#         )
