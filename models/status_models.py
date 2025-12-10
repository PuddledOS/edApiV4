from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class StatusResponse(BaseModel):
    """Response for active status check."""
    Value: bool


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


class DetailedHealthResponse(BaseModel):
    """Response for detailed health information."""
    Health: float
    Shields: float
    ShieldsUp: bool

