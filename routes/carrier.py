from fastapi import APIRouter, HTTPException, Request
from typing import Optional
import logging

from models import (
    CarrierStatsResponse,
    CarrierInfoResponse,
    CarrierFuelResponse,
    CarrierBalanceResponse,
    CarrierJumpRequestResponse,
    CarrierCapacityResponse
)
from utils.journal import get_latest_journal_file, parse_journal_line, find_latest_event
import descriptions as desc

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/carrier", tags=["carrier"])


@router.get('/stats', response_model=CarrierStatsResponse, description=desc.CARRIER_STATS)
async def get_carrier_stats(request: Request):
    """Get current carrier statistics including fuel, capacity, crew, and finances."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')

    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    try:
        return CarrierStatsResponse(**carrier_stats)
    except Exception as e:
        logger.error(f"Error parsing carrier stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing carrier data: {str(e)}")


@router.get('/jump-request', response_model=CarrierJumpRequestResponse, description=desc.CARRIER_JUMP_REQUEST)
async def get_carrier_jump_request(request: Request):
    """Get the most recent carrier jump request information."""
    json_location = request.app.state.json_location

    jump_request = find_latest_event(json_location, 'CarrierJumpRequest')

    if not jump_request:
        raise HTTPException(status_code=404, detail="No carrier jump request found")

    try:
        return CarrierJumpRequestResponse(**jump_request)
    except Exception as e:
        logger.error(f"Error parsing carrier jump request: {e}")
        raise HTTPException(status_code=500, detail=f"Error parsing jump request: {str(e)}")


@router.get('/info', response_model=CarrierInfoResponse, description=desc.CARRIER_INFO)
async def get_carrier_info(request: Request):
    """Get combined carrier information including stats and jump request."""
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    carrier_stats = None
    jump_request = None
    timestamp = None

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in f:
                data = parse_journal_line(line)
                if not data:
                    continue

                event = data.get('event')

                if event == 'CarrierStats':
                    carrier_stats = CarrierStatsResponse(**data)
                    timestamp = data.get('timestamp')

                elif event == 'CarrierJumpRequest':
                    jump_request = CarrierJumpRequestResponse(**data)
                    if not timestamp:
                        timestamp = data.get('timestamp')

        if not carrier_stats and not jump_request:
            raise HTTPException(status_code=404, detail="No carrier information found")

        return CarrierInfoResponse(
            stats=carrier_stats,
            jump_request=jump_request,
            timestamp=timestamp or "unknown"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting carrier info: {e}")
        raise HTTPException(status_code=500, detail=f"Error reading carrier data: {str(e)}")


@router.get('/fuel', response_model=CarrierFuelResponse, description=desc.CARRIER_FUEL)
async def get_carrier_fuel(request: Request ):
    """Get carrier fuel level and jump range."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')
    carrier_fuel_percentage = round( ( ( carrier_stats.get('FuelLevel') /1000 ) * 100), 2)
    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    return CarrierFuelResponse(
        fuel_level=carrier_stats.get('FuelLevel', 0),
        fuel_percentage=carrier_fuel_percentage,
        jump_range_current=carrier_stats.get('JumpRangeCurr', 0),
        jump_range_max=carrier_stats.get('JumpRangeMax', 0),
        carrier_id= carrier_stats.get('CarrierID'),
        callsign= carrier_stats.get('Callsign', 'Unknown')
    )

@router.get('/balance', response_model = CarrierBalanceResponse, description=desc.CARRIER_BALANCE)
async def get_carrier_balance(request: Request ):
    """Get carrier financial information."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')

    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    finance = carrier_stats.get('Finance', {})

    return CarrierBalanceResponse(
        carrier_balance= finance.get('CarrierBalance', 0),
        reserve_balance= finance.get('ReserveBalance', 0),
        available_balance= finance.get('AvailableBalance', 0),
        reserve_percent= finance.get('ReservePercent', 0),
        carrier_name= carrier_stats.get('Name', 'Unknown'),
        callsign= carrier_stats.get('Callsign', 'Unknown')
    )


@router.get('/capacity', response_model=CarrierCapacityResponse, description=desc.CARRIER_CAPACITY)
async def get_carrier_capacity(request: Request):
    """Get carrier space usage and capacity information."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')

    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    space_usage = carrier_stats.get('SpaceUsage', {})

    total = space_usage.get('TotalCapacity', 0)
    free = space_usage.get('FreeSpace', 0)
    used = total - free
    usage_percent = (used / total * 100) if total > 0 else 0

    return CarrierCapacityResponse(
        total_capacity= total,
        used_space= used,
        free_space= free,
        usage_percent= round(usage_percent, 2),
        cargo= space_usage.get('Cargo', 0),
        ship_packs= space_usage.get('ShipPacks', 0),
        module_packs= space_usage.get('ModulePacks', 0),
        crew= space_usage.get('Crew', 0),
        cargo_reserved= space_usage.get('CargoSpaceReserved', 0)
    )


@router.get('/crew', description=desc.CARRIER_CREW)
async def get_carrier_crew(request: Request):
    """Get carrier crew members and their status."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')

    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    crew = carrier_stats.get('Crew', [])

    active_crew = [member for member in crew if member.get('Activated', False)]
    inactive_crew = [member for member in crew if not member.get('Activated', False)]

    return {
        "total_crew_slots": len(crew),
        "active_crew": len(active_crew),
        "inactive_crew": len(inactive_crew),
        "crew_details": crew,
        "active_services": [member.get('CrewRole') for member in active_crew]
    }


@router.get('/services', description=desc.CARRIER_SERVICES)
async def get_carrier_services(request: Request):
    """Get available carrier services."""
    json_location = request.app.state.json_location

    carrier_stats = find_latest_event(json_location, 'CarrierStats')

    if not carrier_stats:
        raise HTTPException(status_code=404, detail="No carrier statistics found")

    crew = carrier_stats.get('Crew', [])

    services = {}
    for member in crew:
        role = member.get('CrewRole', 'Unknown')
        services[role] = {
            "activated": member.get('Activated', False),
            "enabled": member.get('Enabled', False),
            "crew_name": member.get('CrewName', 'Not assigned')
        }

    return {
        "carrier_name": carrier_stats.get('Name', 'Unknown'),
        "callsign": carrier_stats.get('Callsign', 'Unknown'),
        "services": services
    }