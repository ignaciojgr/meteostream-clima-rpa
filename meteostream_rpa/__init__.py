"""Robot académico METEOSTREAM Clima Chile."""

from .config import Settings
from .robot import MeteoStreamRobot

__all__ = ["MeteoStreamRobot", "Settings"]
__version__ = "1.0.0"

