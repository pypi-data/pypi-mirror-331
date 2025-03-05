"""
Transformative: Convert any X to any Y automatically using AI-powered code generation
"""

import importlib.metadata

# Get version from pyproject.toml via package metadata
try:
    __version__ = importlib.metadata.version("transformative")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.0.0-dev"  # Development version when not installed

# Re-export from conversion module
from transformative.conversion.autoconvert import init, convert, create
from transformative.conversion.decorator import autoconvert

__all__ = ['init', 'convert', 'create', 'autoconvert', '__version__']
