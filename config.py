import json
import sys
import logging
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field, validator
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger(__name__)


class Config(BaseModel):
    """Application configuration model."""

    json_location: Path
    json_test_location: Optional[Path] = None
    host: str = "0.0.0.0"
    port: int = Field(5000, ge=1, le=65535)
    workers: int = Field(3, ge=1, le=10)
    debug: bool = False
    output_directory: Path = Field(default_factory=lambda: Path.home() / "Desktop")
    allowed_origins: list[str] = ["*"]
    enable_keyboard_control: bool = True
    language: str = "en"

    @validator('json_location', 'json_test_location', 'output_directory', pre=True)
    def convert_to_path(cls, v):
        """Convert string paths to Path objects."""
        if v and not isinstance(v, Path):
            return Path(v)
        return v

    class Config:
        """Pydantic configuration."""
        json_encoders = {
            Path: str
        }


def get_config_path() -> Path:
    """Get the configuration file path."""
    return Path(__file__).parent / "cfg.json"


def create_default_config() -> None:
    """Create default configuration file and show message to user."""
    config_path = get_config_path()

    default_config = {
        "json_location": "enter location of your elite dangerous log files here",
        "json_test_location": "enter location of backup / testing files",
        "host": "0.0.0.0",
        "port": 5000,
        "workers": 3,
        "debug": False,
        "output_directory": str(Path.home() / "Desktop"),
        "allowed_origins": ["*"],
        "enable_keyboard_control": True,
        "language" : "en"
    }

    with open(config_path, 'w') as file:
        json.dump(default_config, file, indent=4, ensure_ascii=False)

    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo(
        "Config File Missing",
        f"Elite Dangerous API Tool\n\n"
        f"A new config file has been created at:\n{config_path}\n\n"
        f"Please edit the json_location value to point to your Elite Dangerous log files before running again.\n\n"
        f"Author: Cmdr Puddled"
    )
    root.destroy()
    logger.info(f"Default config created at {config_path}")
    sys.exit(0)


def load_config() -> Config:
    """Load and validate configuration from file."""
    config_path = get_config_path()

    if not config_path.exists():
        create_default_config()

    try:
        with open(config_path, "r") as f:
            data = json.load(f)
            return Config(**data)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        sys.exit(1)
