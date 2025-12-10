from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class KeySendResponse(BaseModel):
    """Response for keyboard control."""
    status: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None
