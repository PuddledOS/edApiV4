from fastapi import APIRouter, HTTPException, Request
import logging

from models import ShipResponse, LoadoutResponse
from utils.journal import find_latest_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ships", tags=["ships"])


@router.get('/current', response_model=ShipResponse)
async def get_current_ship(request: Request):
    """Get information about the current ship."""
    json_location = request.app.state.json_location

    loadout_event = find_latest_event(json_location, 'Loadout')

    if not loadout_event:
        raise HTTPException(status_code=404, detail="No ship loadout found")

    return ShipResponse(
        Ship=loadout_event.get('Ship'),
        ShipName=loadout_event.get('ShipName'),
        ShipIdent=loadout_event.get('ShipIdent'),
        HullValue=loadout_event.get('HullValue'),
        ModulesValue=loadout_event.get('ModulesValue'),
        Rebuy=loadout_event.get('Rebuy')
    )


@router.get('/loadout')
async def get_loadout(request: Request):
    """Get complete ship loadout with modules."""
    json_location = request.app.state.json_location

    loadout_event = find_latest_event(json_location, 'Loadout')

    if not loadout_event:
        raise HTTPException(status_code=404, detail="No ship loadout found")

    return {
        "ship": loadout_event.get('Ship'),
        "modules": loadout_event.get('Modules', []),
        "fuel_capacity": loadout_event.get('FuelCapacity'),
        "cargo_capacity": loadout_event.get('CargoCapacity')
    }