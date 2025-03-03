from typing import Any, Dict
import pydantic

class _CallPacket(pydantic.BaseModel):
    procedure: str
    data: Dict[str, Any] = {}

class _ClientPacket(pydantic.BaseModel):
    data: str
