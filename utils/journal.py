import json
import glob
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from collections import defaultdict

logger = logging.getLogger(__name__)


def get_latest_journal_file(json_location: Path) -> Optional[Path]:
    """
    Get the most recent journal file.

    Args:
        json_location: Directory containing journal files

    Returns:
        Path to the latest journal file or None
    """
    try:
        pattern = str(json_location / 'Journal*.log')
        files = sorted(glob.iglob(pattern), key=lambda x: Path(x).stat().st_ctime, reverse=True)
        return Path(files[0]) if files else None
    except Exception as e:
        logger.error(f"Error getting latest journal file: {e}")
        return None


def get_all_journal_files(json_location: Path, reverse: bool = False) -> List[Path]:
    """
    Get all journal files sorted by creation time.

    Args:
        json_location: Directory containing journal files
        reverse: If True, sort newest first

    Returns:
        List of journal file paths
    """
    try:
        pattern = str(json_location / 'Journal*.log')
        files = sorted(
            glob.glob(pattern),
            key=lambda x: Path(x).stat().st_ctime,
            reverse=reverse
        )
        return [Path(f) for f in files]
    except Exception as e:
        logger.error(f"Error getting journal files: {e}")
        return []


def parse_journal_line(line: str) -> Optional[Dict[str, Any]]:
    """
    Parse a single line from a journal file.

    Args:
        line: Line from journal file

    Returns:
        Parsed JSON data or None if invalid
    """
    line = line.strip()
    if not line or not line.startswith('{'):
        return None

    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None


def find_latest_event(json_location: Path, event_name: str) -> Optional[Dict[str, Any]]:
    """
    Find the most recent occurrence of a specific event.

    Args:
        json_location: Directory containing journal files
        event_name: Name of the event to find

    Returns:
        Event data or None if not found
    """
    journal_file = get_latest_journal_file(json_location)
    if not journal_file:
        return None

    try:
        with open(journal_file, 'r') as f:
            for line in reversed(list(f)):
                data = parse_journal_line(line)
                if data and data.get('event') == event_name:
                    return data
    except Exception as e:
        logger.error(f"Error reading journal file: {e}")

    return None


def process_all_journals(
        json_location: Path,
        event_type: str,
        processor_func: Callable[[Dict[str, Any], Path], Any]
) -> List[Any]:
    """
    Process all journal files for a specific event type.

    Args:
        json_location: Directory containing journal files
        event_type: Type of event to process
        processor_func: Function to process each matching event

    Returns:
        List of processed results
    """
    results = []
    journal_files = get_all_journal_files(json_location)

    for filepath in journal_files:
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    entry = parse_journal_line(line)
                    if entry and entry.get('event') == event_type:
                        try:
                            result = processor_func(entry, filepath)
                            if result:
                                results.append(result)
                        except Exception as e:
                            logger.error(f"Error processing event in {filepath}: {e}")
        except IOError as e:
            logger.error(f"Error reading {filepath}: {e}")

    return results


def calculate_cargo_inventory(json_location: Path) -> Dict[str, int]:
    """
    Calculate current cargo inventory from transfer history.

    Args:
        json_location: Directory containing journal files

    Returns:
        Dictionary with item types as keys and quantities as values
    """
    inventory = defaultdict(int)
    journal_files = get_all_journal_files(json_location)

    for filepath in journal_files:
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    entry = parse_journal_line(line)
                    if not entry or entry.get('event') != 'CargoTransfer':
                        continue

                    transfers = entry.get('Transfers', [])
                    for transfer in transfers:
                        item_type = transfer.get('Type', '')
                        count = transfer.get('Count', 0)
                        direction = transfer.get('Direction', '')

                        if direction == 'tocarrier':
                            inventory[item_type] += count
                        elif direction == 'toship':
                            inventory[item_type] -= count
        except Exception as e:
            logger.error(f"Error processing {filepath}: {e}")

    return dict(inventory)

