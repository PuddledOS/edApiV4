from fastapi import APIRouter, Query, HTTPException, Request
from pathlib import Path
import logging

from models import (
    StatusResponse, BalanceResponse, FlagsResponse,
    ScreenResponse, PipsResponse, FuelResponse, DetailedHealthResponse
)
from utils.file_utils import read_json_file
from utils.journal import find_latest_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/status", tags=["status"])


def get_json_location(request: Request) -> Path:
    """Get JSON location from app state."""
    return request.app.state.json_location


@router.get('/active', response_model=StatusResponse)
async def get_active(request: Request):
    """Check if Elite Dangerous is currently running."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    # Check if Flags2 exists (indicates game is running)
    is_running = 'Flags2' in data
    value = 'running' if is_running else 'shutdown'

    return StatusResponse(Value=value)


@router.get('/wealth', response_model=BalanceResponse)
async def get_wealth(request: Request):
    """Get current balance/wealth."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    balance = data.get('Balance', '0')
    return BalanceResponse(Balance=str(balance))


@router.get('/flags', response_model=FlagsResponse)
async def get_flags(request: Request):
    """Get current status flags."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    # Process Flags (32-bit)
    flags = data.get('Flags', 0)
    formatted_flags = format(flags, '032b')[::-1]

    # Process Flags2 (19-bit)
    flags2 = data.get('Flags2', 0)
    formatted_flags2 = format(flags2, '019b')[::-1]

    return FlagsResponse(flags=formatted_flags, flags2=formatted_flags2)


@router.get('/screen', response_model=ScreenResponse)
async def get_screen(request: Request):
    """Get current GUI focus/screen."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    focus = data.get('GuiFocus', '0')
    return ScreenResponse(Focus=str(focus))


@router.get('/pips', response_model=PipsResponse, description="Request parameters should be raw or percent.\nRaw will return a single digit number 0 - 8, percent will return a value between 0 - 100 dependant upon current setting ")
async def get_pips(request: Request, type: str = Query('percent', regex='^(percent|raw)$', description="Request either percentage value or raw value" ) ):
    """Get power distribution (pips) information."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    pips = data.get('Pips', [0, 0, 0])

    if type == 'percent':
        return PipsResponse(
            Systems=(pips[0] * 100) / 8,
            Engines=(pips[1] * 100) / 8,
            Weapons=(pips[2] * 100) / 8
        )
    else:
        # type is raw
        return PipsResponse(
            Systems=float(pips[0]),
            Engines=float(pips[1]),
            Weapons=float(pips[2])
        )


@router.get('/fuel', response_model=FuelResponse)
async def get_fuel(request: Request):
    """Get fuel information."""
    json_location = get_json_location(request)
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    fuel = data.get('Fuel', {'FuelMain': 0})
    fuel_main = fuel.get('FuelMain', 0)

    # Get fuel capacity from journal
    loadout_event = find_latest_event(json_location, 'Loadout')
    fuel_capacity = 0

    if loadout_event:
        fuel_capacity = loadout_event.get('FuelCapacity', {}).get('Main', 0)

    # Calculate percentage
    fuel_percentage = round(100 * (fuel_main / fuel_capacity), 0) if fuel_capacity > 0 else 0

    return FuelResponse(
        Capacity=fuel_capacity,
        Level=fuel_main,
        Percentage=fuel_percentage
    )


@router.get('/health-detailed', response_model=DetailedHealthResponse)
async def get_detailed_health(request: Request):
    """Get detailed health information including shields and hull."""
    json_location = request.app.state.json_location
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    health = data.get('Health', 1.0)
    shields = data.get('Shields', 0.0)

    return DetailedHealthResponse(
        Health=health,
        Shields=shields,
        ShieldsUp=data.get('ShieldsUp', False)
    )