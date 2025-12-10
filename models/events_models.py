from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class PriceResponse(BaseModel):
    """Response for buy price queries."""
    Price: str

class MessageItem(BaseModel):
    """Individual message item."""
    From: str
    From_Localised: str
    Message: str
    Message_Localised: str
    Channel: str


class EventResponse(BaseModel):
    """Generic event response."""
    Value: Optional[str] = None
    Station: Optional[str] = None
    Time: Optional[str] = None
