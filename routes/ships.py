from fastapi import APIRouter, HTTPException, Request
import logging

from models import ShipResponse, LoadoutResponse, ShipModulesResponse
from utils.file_utils import read_json_file
from utils.journal import find_latest_event
import descriptions as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ships", tags=["ships"])


@router.get('/current', response_model=ShipResponse, description=desc.SHIPS_CURRENT)
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


@router.get('/loadout', response_model=LoadoutResponse, description=desc.SHIPS_LOADOUT)
async def get_loadout(request: Request):
    """Get complete ship loadout with modules."""
    json_location = request.app.state.json_location

    loadout_event = find_latest_event(json_location, 'Loadout')

    if not loadout_event:
        raise HTTPException(status_code=404, detail="No ship loadout found")

    return LoadoutResponse(
        ship= loadout_event.get('Ship'),
        modules= loadout_event.get('Modules', []),
        fuel_capacity= loadout_event.get('FuelCapacity'),
        cargo_capacity= loadout_event.get('CargoCapacity')
    )

@router.get('/ship-modules', response_model=ShipModulesResponse, description=desc.SHIP_MODULES)
async def get_ship_modules(request: Request):
    """Get list of installed ship modules."""
    json_location = request.app.state.json_location
    modules_file = json_location / 'ModulesInfo.json'

    modules_data = read_json_file(modules_file)
    if not modules_data:
        raise HTTPException(status_code=404, detail="Cannot read modules file")

    return ShipModulesResponse(
        timestamp= modules_data.get('timestamp'),
        event= modules_data.get('event'),
        modules= modules_data.get('Modules', [])
    )
