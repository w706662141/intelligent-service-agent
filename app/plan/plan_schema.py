from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field


class Step(BaseModel):
    step_id: int = Field(..., description='步骤编号')
    tool: str = Field(..., description='要调用的工具名')
    description: str = Field(..., description='步骤说明')
    args: Dict[str, Any] = Field(default_factory=dict, description='工具参数')
    depends_on: Optional[List[int]] = Field(default=None, description='依赖的步骤')


class Plan(BaseModel):
    steps: List[Step]
