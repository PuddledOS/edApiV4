from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class LocationResponse(BaseModel):
    """Response for current location."""
    StarSystem: str
    SystemAddress: Optional[int] = None
    StarPos: list = []
    Body: Optional[str] = None
    BodyType: Optional[str] = None
    Docked: bool = False
    StationName: Optional[str] = None

class JumpHistoryResponse(BaseModel):
    system: str
    timestamp: str
    jump_dist: Optional[float] = None
    fuel_used: Optional[float] = None

class NavRouteResponse(BaseModel):
    timestamp: str
    event: str
    route: list = []
