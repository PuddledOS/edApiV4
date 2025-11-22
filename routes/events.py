from fastapi import APIRouter, HTTPException, Query, Request
from pathlib import Path
from typing import List, Optional
import logging

from models import EventResponse, MessageItem, PriceResponse
from utils.journal import get_latest_journal_file, parse_journal_line

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/events", tags=["events"])


def get_json_location(request: Request) -> Path:
    """Get JSON location from app state."""
    return request.app.state.json_location


@router.get('/messages', response_model=List[MessageItem])
async def get_messages(request: Request,
        count: int = Query(10, ge=1, le=100, description="Number of messages to retrieve"),
        channel: str = Query('npc', regex='^(npc|starsystem|squadron)$', description="Message channel")
):
    """Get recent messages from specified channel."""
    json_location = get_json_location(request)
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    messages = []
    remaining = count

    try:
        with open(journal_file, 'r') as f:
            for line in reversed(list(f)):
                if remaining <= 0:
                    break

                data = parse_journal_line(line)
                if not data:
                    continue

                if data.get('event') == 'ReceiveText' and data.get('Channel') == channel:
                    from_localised = data.get('From_Localised', data.get('From', ''))
                    from_localised = from_localised.replace('$EXT_PANEL_ColonisationShip;', 'Colonisation Ship : ')

                    message = MessageItem(
                        From=data.get('From', ''),
                        From_Localised=from_localised,
                        Message=data.get('Message', ''),
                        Message_Localised=data.get('Message_Localised', ''),
                        Channel=data.get('Channel', '')
                    )
                    messages.append(message)
                    remaining -= 1
    except Exception as e:
        logger.error(f"Error reading messages: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")

    return messages


@router.get('/event', response_model=EventResponse)
async def get_event(request: Request,
        event_name: str = Query(..., description="Event name to search for"),
        property_name: str = Query(..., description="Property to extract from event")
):
    """Get latest occurrence of a specific event and extract a property."""
    json_location = get_json_location(request)
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    try:
        with open(journal_file, 'r') as f:
            for line in reversed(list(f)):
                data = parse_journal_line(line)
                if not data or data.get('event') != event_name:
                    continue

                # Found the event
                if event_name in ('Undocked', 'Docked'):
                    return EventResponse(
                        Station=data.get(property_name),
                        Time=data.get('timestamp')
                    )
                else:
                    return EventResponse(Value=str(data.get(property_name, 'No Data')))

        # Event not found
        return EventResponse(Value='No Data')

    except Exception as e:
        logger.error(f"Error searching for event: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")


@router.get('/buy-price', response_model=PriceResponse)
async def get_buy_price(request: Request,
        event_name: str = Query(..., description="Event name (e.g., MarketBuy)"),
        item_type: str = Query(..., description="Item type to find price for")
):
    """Get the buy price for a specific item from recent events."""
    json_location = get_json_location(request)
    journal_file = get_latest_journal_file(json_location)

    if not journal_file:
        raise HTTPException(status_code=404, detail="No journal file found")

    try:
        with open(journal_file, 'r') as f:
            for line in reversed(list(f)):
                data = parse_journal_line(line)
                if not data:
                    continue

                if (data.get('event') == event_name and
                        data.get('Type', '').lower() == item_type.lower()):
                    return PriceResponse(Price=str(data.get('BuyPrice', '0')))

        # Not found
        return PriceResponse(Price='0')

    except Exception as e:
        logger.error(f"Error searching for price: {e}")
        raise HTTPException(status_code=500, detail="Error reading journal file")

