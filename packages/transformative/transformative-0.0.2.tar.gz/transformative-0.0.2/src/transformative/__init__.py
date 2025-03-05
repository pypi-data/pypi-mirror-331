"""
Transformative: Convert any X to any Y automatically using AI-powered code generation
"""

from pathlib import Path
from typing import Optional, Union
import importlib.metadata

# Get version from pyproject.toml via package metadata
try:
    __version__ = importlib.metadata.version("transformative")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.1"  # Default during development

# Re-export from conversion module
from ..conversion.transformative import init, convert, create
from ..conversion.decorator import autoconvert

__all__ = ['init', 'convert', 'create', 'autoconvert', '__version__']
