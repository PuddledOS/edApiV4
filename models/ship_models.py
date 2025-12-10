from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

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


class ShipLoadout(BaseModel):
    """Ship load out."""
    ship: str
    modules: List[Any]
    fuel_capacity: int
    cargo_capacity: int

class ShipModulesResponse(BaseModel):
    timestamp: str
    event: str
    modules: list = []