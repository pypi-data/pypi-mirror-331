from __future__ import annotations
from importlib.metadata import version

__version__ = version(__name__)

from .ara_vision import ARAVisionManager
from .ara_core import ARALinkManager

import sys
from pathlib import Path

__all__ = ["ARAVisionManager", "ARALinkManager"]

sys.path.append(str(Path(__file__).resolve().parent))
