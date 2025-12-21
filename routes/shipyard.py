from fastapi import APIRouter, HTTPException, Request, Query
from pathlib import Path
from typing import Dict, Any
import logging

from models.shipyard_models import ShipyardResponse, ShipyardLockerResponse
from utils.file_utils import read_json_file
import lang.descriptions_en as desc


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/shipyard", tags=["shipyard"])

def get_json_location(request: Request) -> Path:
    """Get JSON location from app state."""
    return request.app.state.json_location

def read_json_data_file(request: Request, file_to_read: str) -> Dict[str, Any]:
    json_location = get_json_location(request)
    status_file = json_location / file_to_read
    data = read_json_file(status_file)
    return data

@router.get("/get-ships", response_model=ShipyardResponse)
async def get_shipyards(request: Request) -> ShipyardResponse:
    data = read_json_data_file(request, 'Shipyard.json')
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    return ShipyardResponse(
        timestamp = data.get('timestamp'),
        event= data.get('event'),
        marketID= data.get('MarketID'),
        station_name= data.get('StationName'),
        star_system= data.get('StarSystem'),
        pricelist= data.get('PriceList'),
    )

@router.get("/get-ship-locker", response_model=ShipyardLockerResponse)
async def get_shipyard_locker(request: Request) -> ShipyardLockerResponse:
    data = read_json_data_file(request, 'ShipLocker.json')
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    return ShipyardLockerResponse(
        timestamp = data.get('timestamp'),
        event= data.get('event'),
        items= data.get('Items'),
        components= data.get('Components'),
        consumables= data.get('Consumables'),
        data= data.get('Data'),
    )
