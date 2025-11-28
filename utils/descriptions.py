import importlib
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


class DescriptionLoader:
    """Load descriptions based on language setting."""

    def __init__(self, language: str = "en"):
        """
        Initialize description loader.

        Args:
            language: Language code (en, fr, de, es, etc.)
        """
        self.language = language
        self._module = None
        self._load_language(language)

    def _load_language(self, language: str):
        """Load the appropriate language module."""
        try:
            module_name = f"descriptions_{language}"
            self._module = importlib.import_module(module_name)
            logger.info(f"Loaded descriptions for language: {language}")
        except ImportError:
            logger.warning(f"Language '{language}' not found, falling back to English")
            try:
                self._module = importlib.import_module("descriptions_en")
            except ImportError:
                logger.error("English fallback not found!")
                raise

    def __getattr__(self, name: str) -> Any:
        """Get description attribute from loaded module."""
        if self._module is None:
            raise RuntimeError("No description module loaded")

        try:
            return getattr(self._module, name)
        except AttributeError:
            logger.warning(f"Description '{name}' not found in {self.language}")
            return f"Description not available ({name})"

    def reload(self, language: str):
        """Reload descriptions with a different language."""
        self._load_language(language)
        self.language = language


class DescriptionProxy:
    """
    Proxy that safely accesses the global description loader.

    This allows routes to import 'desc' at module level without errors,
    even before the loader is initialized.
    """

    def __getattr__(self, name: str) -> str:
        """Get description, handling None case gracefully."""
        global _desc_loader
        if _desc_loader is None:
            # Return empty string if not initialized yet
            # This allows routes to be imported before initialization
            logger.debug(f"Description '{name}' accessed before initialization")
            return ""
        return getattr(_desc_loader, name)


# Private instance that gets initialized in main.py
_desc_loader: Optional[DescriptionLoader] = None

# Public proxy that's always safe to access
desc = DescriptionProxy()


def init_descriptions(language: str = "en") -> DescriptionLoader:
    """
    Initialize the global description loader.

    This should be called once during application startup.
    """
    global _desc_loader
    _desc_loader = DescriptionLoader(language)
    logger.info(f"Descriptions initialized with language: {language}")
    return _desc_loader


def get_current_language() -> Optional[str]:
    """Get the current language or None if not initialized."""
    if _desc_loader is None:
        return None
    return _desc_loader.language