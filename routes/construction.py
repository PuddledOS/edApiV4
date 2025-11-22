from fastapi import APIRouter, HTTPException, Request
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from models import ConstructionResponse
from utils.journal import get_latest_journal_file, parse_journal_line

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/construction", tags=["construction"])


def get_json_location(request: Request) -> Path:
    """Get JSON location from app state."""
    return request.app.state.json_location


@router.get('/current', response_model=ConstructionResponse)
async def get_construction(request: Request):
    """Get current construction depot information."""
    json_location = get_json_location(request)
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    construction_data = None
    market_id = None
    construction_complete = False

    # Find construction depot event
    try:
        with open(journal_file, 'r') as f:
            for line in f:
                data = parse_journal_line(line)
                if data and data.get('event') == 'ColonisationConstructionDepot':
                    construction_data = data.get('ResourcesRequired', [])
                    market_id = data.get('MarketID')
                    construction_complete = data.get('ConstructionComplete', False)
    except Exception as e:
        logger.error(f"Error reading construction data: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")

    if not construction_data:
        return ConstructionResponse(
            name='no data',
            system='no data',
            data='no data'
        )

    # Find station name and system
    station_name = 'no data'
    system_name = 'no data'

    if market_id:
        try:
            with open(journal_file, 'r') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if (data and data.get('event') == 'Docked' and
                            data.get('MarketID') == market_id):
                        station_name = data.get('StationName', 'no data')
                        station_name = station_name.replace('$EXT_PANEL_ColonisationShip;', 'Colonisation Ship : ')
                        system_name = data.get('StarSystem', 'no data')
                        break
        except Exception as e:
            logger.error(f"Error finding station name: {e}")

    return ConstructionResponse(
        id=market_id,
        name=station_name,
        complete=construction_complete,
        system=system_name,
        data=construction_data
    )
