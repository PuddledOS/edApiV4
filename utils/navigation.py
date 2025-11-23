import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from utils.journal import get_latest_journal_file, parse_journal_line

logger = logging.getLogger(__name__)


def calculate_distance(pos1: List[float], pos2: List[float]) -> float:
    """Calculate distance between two 3D coordinates."""
    if len(pos1) != 3 or len(pos2) != 3:
        return 0.0

    return ((pos1[0] - pos2[0]) ** 2 +
            (pos1[1] - pos2[1]) ** 2 +
            (pos1[2] - pos2[2]) ** 2) ** 0.5


def get_visited_systems(json_location: Path, limit: int = 50) -> List[str]:
    """Get list of recently visited systems."""
    journal_file = get_latest_journal_file(json_location)
    if not journal_file:
        return []

    systems = []

    try:
        with open(journal_file, 'r', encoding='utf-8') as f:
            for line in reversed(list(f)):
                if len(systems) >= limit:
                    break

                data = parse_journal_line(line)
                if data and data.get('event') == 'FSDJump':
                    system = data.get('StarSystem')
                    if system and system not in systems:
                        systems.append(system)
    except Exception as e:
        logger.error(f"Error getting visited systems: {e}")

    return systems