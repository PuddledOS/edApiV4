from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional, Dict, Any
import logging

from models import LocationResponse, JumpHistoryResponse
from utils.file_utils import read_json_file
from utils.journal import get_latest_journal_file, parse_journal_line

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/navigation", tags=["navigation"])


@router.get('/current-location', response_model=LocationResponse)
async def get_current_location(request: Request):
    """Get current system and location."""
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in reversed(list(f)):
                data = parse_journal_line(line)
                if not data:
                    continue

                # Look for location events
                if data.get('event') in ('Location', 'FSDJump', 'CarrierJump'):
                    return LocationResponse(
                        StarSystem=data.get('StarSystem', 'Unknown'),
                        SystemAddress=data.get('SystemAddress'),
                        StarPos=data.get('StarPos', []),
                        Body=data.get('Body'),
                        BodyType=data.get('BodyType'),
                        Docked=data.get('Docked', False),
                        StationName=data.get('StationName')
                    )

        return LocationResponse(
            StarSystem='Unknown',
            SystemAddress=None,
            StarPos=[],
            Body=None,
            BodyType=None,
            Docked=False,
            StationName=None
        )

    except Exception as e:
        logger.error(f"Error getting location: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")


@router.get('/jump-history')
async def get_jump_history(
        request: Request,
        limit: int = Query(10, ge=1, le=100, description="Number of jumps to retrieve")
) -> list[Dict[str, Any]]:
    """Get recent jump history."""
    json_location = request.app.state.json_location
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    jumps = []

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in reversed(list(f)):
                if len(jumps) >= limit:
                    break

                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'FSDJump':
                    jumps.append({
                        'system': data.get('StarSystem'),
                        'timestamp': data.get('timestamp'),
                        'jump_dist': data.get('JumpDist'),
                        'fuel_used': data.get('FuelUsed')
                    })

        return jumps

    except Exception as e:
        logger.error(f"Error getting jump history: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")


@router.get('/nearest-station')
async def get_nearest_station(request: Request):
    """Get information about the nearest station."""
    json_location = request.app.state.json_location
    status_file = json_location / 'Status.json'

    data = read_json_file(status_file)
    if not data:
        raise HTTPException(status_code=503, detail="Cannot read status file")

    # to be completed
    return {
        "message": "Nearest station endpoint",
        "docked": data.get('Docked', False)
    }