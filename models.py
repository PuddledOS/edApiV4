from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StatusResponse(BaseModel):
    """Response for active status check."""
    Value: str


class BalanceResponse(BaseModel):
    """Response for wealth/balance query."""
    Balance: str


class FlagsResponse(BaseModel):
    """Response for flags query."""
    flags: str
    flags2: str


class ScreenResponse(BaseModel):
    """Response for current screen/GUI focus."""
    Focus: str


class PipsResponse(BaseModel):
    """Response for power distribution (pips)."""
    Systems: float
    Engines: float
    Weapons: float


class FuelResponse(BaseModel):
    """Response for fuel information."""
    Capacity: float
    Level: float
    Percentage: float


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


class PriceResponse(BaseModel):
    """Response for buy price queries."""
    Price: str


class ConstructionResponse(BaseModel):
    """Response for construction data."""
    id: Optional[str] = None
    name: str
    complete: bool = False
    system: str
    data: Any


class KeySendResponse(BaseModel):
    """Response for keyboard control."""
    status: Optional[str] = None
    error: Optional[str] = None
    details: Optional[str] = None


class ExportTaskResponse(BaseModel):
    """Response for export task initiation."""
    task_id: str
    status: str
    message: str


class TaskStatusResponse(BaseModel):
    """Response for task status check."""
    task_id: str
    status: str
    progress: Optional[str] = None
    error: Optional[str] = None

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

class DetailedHealthResponse(BaseModel):
    """Response for detailed health information."""
    Health: float
    Shields: float
    ShieldsUp: bool

class ShipResponse(BaseModel):
    """Response for current ship information."""
    Ship: str
    ShipName: Optional[str] = None
    ShipIdent: Optional[str] = None
    HullValue: Optional[int] = None
    ModulesValue: Optional[int] = None
    Rebuy: Optional[int] = None

class LoadoutResponse(BaseModel):
    ship: str
    modules: List[Dict[str, Any]]
    fuel_capacity: Optional[Dict[str, float]] = None
    cargo_capacity: Optional[int] = None

