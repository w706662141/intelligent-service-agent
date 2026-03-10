from typing import Dict, Optional

from pydantic import BaseModel


class ToolCall(BaseModel):
    tool_name: str
    arguments: Dict


class ActionResponse(BaseModel):
    tool_call: Optional[ToolCall] = None
