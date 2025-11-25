from fastapi import APIRouter, HTTPException, Query, Request
from pathlib import Path
from typing import List, Dict, Any
import logging

from utils.file_utils import read_json_file
from utils.journal import calculate_cargo_inventory
import descriptions as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cargo", tags=["cargo"])


def get_json_location(request: Request) -> Path:
    """Get JSON location from app state."""
    return request.app.state.json_location


@router.get('/inventory', description=desc.CARGO_INVENTORY)
async def get_cargo(request: Request) -> List[Dict[str, Any]]:
    """Get current cargo inventory."""
    json_location = get_json_location(request)
    cargo_file = json_location / 'Cargo.json'

    data = read_json_file(cargo_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read cargo file")

    return data.get('Inventory', [])


@router.get('/market')
async def get_market(request: Request) -> List[Dict[str, Any]]:
    """Get current market data."""
    json_location = get_json_location(request)
    market_file = json_location / 'Market.json'

    data = read_json_file(market_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read market file")

    return data.get('Items', [])


@router.get('/transfer-history', description=desc.CARGO_TRANSFER_HISTORY)
async def get_transfer_history(request: Request) -> Dict[str, int]:
    """
    Calculate current cargo inventory from all transfer history.
    Returns net quantities for each item type.
    """
    json_location = get_json_location(request)
    inventory = calculate_cargo_inventory(json_location)
    return inventory
