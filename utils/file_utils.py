import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


def read_json_file(filepath: Path) -> Optional[Dict[str, Any]]:
    """
    Safely read and parse a JSON file.

    Args:
        filepath: Path to the JSON file

    Returns:
        Parsed JSON data or None if error occurs
    """
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {filepath}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error reading {filepath}: {e}")
        return None


def write_json_file(filepath: Path, data: Any, append: bool = False) -> bool:
    """
    Write data to a JSON file.

    Args:
        filepath: Path to the JSON file
        data: Data to write
        append: Whether to append to existing file

    Returns:
        True if successful, False otherwise
    """
    try:
        mode = 'a' if append else 'w'
        with open(filepath, mode) as f:
            json.dump(data, f)
            if append:
                f.write('\n')
        return True
    except Exception as e:
        logger.error(f"Error writing to {filepath}: {e}")
        return False


def ensure_directory(directory: Path) -> bool:
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        directory: Path to the directory

    Returns:
        True if directory exists or was created successfully
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {e}")
        return False

