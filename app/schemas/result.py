from dataclasses import dataclass, asdict
from typing import Optional, Any

from app.schemas.error import ErrorType


@dataclass
class ToolResult:
    success: bool
    error_type: ErrorType
    message: str
    data: Optional[Any] = None

    def to_dict(self) -> dict:
        result = asdict(self)
        result['error_type'] = self.error_type.value
        return result
