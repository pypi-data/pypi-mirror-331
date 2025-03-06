"""Template for a simple Github workflow for a Python package built for distribution."""

import importlib.metadata

try:
    __version__ = importlib.metadata.version('cicd_tempy')
except importlib.metadata.PackageNotFoundError:
    __version__ = '0.0.0'  # Default if package is not installed
