from abc import ABC, abstractmethod
from typing import Optional, Dict

from pydantic import BaseModel


class ToolInput(BaseModel):
    pass


class ToolOutput(BaseModel):
    success: bool
    message: str
    data: Optional[Dict] = None


class BaseTool(ABC):
    name: str
    description: str
    input_model: type[ToolInput]

    @abstractmethod
    def run(self, input_data: ToolInput) -> ToolOutput:
        pass
