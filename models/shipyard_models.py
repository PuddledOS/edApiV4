from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ShipyardResponse(BaseModel):
    timestamp: str
    event: str
    marketID: int
    station_name: str
    star_system: str
    pricelist: List = []

class ShipyardLockerResponse(BaseModel):
    timestamp: str
    event: str
    items: List = []
    components: List = []
    consumables: List = []
    data: List = []