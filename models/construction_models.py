from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ConstructionResponse(BaseModel):
    """Response for construction data."""
    id: Optional[str] = None
    name: str
    complete: bool = False
    system: str
    data: Any
