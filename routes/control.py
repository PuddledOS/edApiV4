from fastapi import APIRouter, Query, Request
import logging

from models.control_models import KeySendResponse
from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/control", tags=["control"])

keyboard_controller = Controller()


@router.post('/sendkey', response_model=KeySendResponse)
async def send_key(
        request: Request,
        key: str = Query(...),
        modifier: str = Query('', regex='^(|shift|ctrl|alt)$')
):
    """Send a keyboard key press to the system."""
    if not request.app.state.config.enable_keyboard_control:
        return KeySendResponse(
            error="Keyboard control is disabled",
            details="Enable in configuration file"
        )

    if not key:
        return KeySendResponse(error="No key provided")

    try:
        if modifier:
            mod_key = {
                'shift': Key.shift,
                'ctrl': Key.ctrl,
                'alt': Key.alt
            }.get(modifier)

            if not mod_key:
                return KeySendResponse(error=f"Invalid modifier: {modifier}")

            with keyboard_controller.pressed(mod_key):
                keyboard_controller.press(key)
                keyboard_controller.release(key)
        else:
            keyboard_controller.press(key)
            keyboard_controller.release(key)

        modifier_str = f"{modifier} + " if modifier else ""
        return KeySendResponse(status=f"Key '{modifier_str}{key}' sent successfully")
    except Exception as e:
        logger.error(f"Error sending key: {e}")
        return KeySendResponse(error="Failed to send key", details=str(e))

