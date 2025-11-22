from fastapi import APIRouter, HTTPException, Request
import logging
import traceback

from models import ConstructionResponse
from utils.journal import get_latest_journal_file, parse_journal_line

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/construction", tags=["construction"])


@router.get('/current', response_model=ConstructionResponse)
async def get_construction(request: Request):
    """Get current construction depot information."""
    try:
        json_location = request.app.state.json_location
        logger.info(f"Looking for journal files in: {json_location}")

        journal_file = get_latest_journal_file(json_location)

        if not journal_file:
            logger.warning("No journal file found")
            raise HTTPException(status_code=404, detail="No journal file found")

        logger.info(f"Reading journal file: {journal_file}")

        construction_data = None
        market_id = None
        construction_complete = False

        try:
            with open(journal_file, 'r', encoding='utf-8') as f:
                for line in f:
                    data = parse_journal_line(line)
                    if data and data.get('event') == 'ColonisationConstructionDepot':
                        construction_data = data.get('ResourcesRequired', [])
                        market_id = data.get('MarketID')
                        construction_complete = data.get('ConstructionComplete', False)
                        logger.info(f"Found construction depot: MarketID={market_id}, Complete={construction_complete}")
                        # Keep looking to find the most recent one
        except Exception as e:
            logger.error(f"Error reading construction data: {e}")
            logger.error(traceback.format_exc())
            raise HTTPException(status_code=500, detail=f"Error reading journal file: {str(e)}")

        if not construction_data:
            logger.info("No construction data found, returning 'no data'")
            return ConstructionResponse(
                id=None,
                name='no data',
                complete=False,
                system='no data',
                data='no data'
            )

        station_name = 'no data'
        system_name = 'no data'

        if market_id:
            try:
                with open(journal_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        data = parse_journal_line(line)
                        if (data and data.get('event') == 'Docked' and
                                data.get('MarketID') == market_id):
                            station_name = data.get('StationName', 'no data')
                            station_name = station_name.replace('$EXT_PANEL_ColonisationShip;', 'Colonisation Ship : ')
                            system_name = data.get('StarSystem', 'no data')
                            logger.info(f"Found station: {station_name} in {system_name}")
                            break
            except Exception as e:
                logger.error(f"Error finding station name: {e}")
                # Don't fail the whole request if we can't find the station name

        # Convert market_id to string if it's an integer
        market_id_str = str(market_id) if market_id is not None else None

        return ConstructionResponse(
            id=market_id_str,
            name=station_name,
            complete=construction_complete,
            system=system_name,
            data=construction_data
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_construction: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get('/test')
async def test_construction(request: Request):
    """Test endpoint to check if construction route is working."""
    return {
        "status": "ok",
        "json_location": str(request.app.state.json_location),
        "message": "Construction router is working"
    }