from typing import Any, Dict, Optional, List

from pydantic import BaseModel, Field


class Step(BaseModel):
    step_id: int = Field(..., description='步骤编号')
    type: str = Field(..., description='步骤调用tool,llm,react哪一个')
    tool: Optional[str] = Field(default=None, description='要调用的工具名')
    description: str = Field(..., description='步骤说明')
    args: Dict[str, Any] = Field(default_factory=dict, description='工具参数')
    depends_on: Optional[List[int]] = Field(default=None, description='依赖的步骤')

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "description": self.description,
            "type": self.type,
            "tool": self.tool,
            "args": self.args,
            "depends_on": self.depends_on
        }


class Plan(BaseModel):
    steps: List[Step]
