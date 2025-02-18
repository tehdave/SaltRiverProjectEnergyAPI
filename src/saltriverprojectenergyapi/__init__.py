"""Init file for Salt River Project unofficial API."""

import logging

from .client import SaltRiverProjectClient  # noqa: F401

__version__ = '1.0.5'

# Create a logger for the package
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create and set a formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the handler if not already added
if not logger.handlers:
    logger.addHandler(ch)
    logger.propagate = False  # Prevent double logging if used in a larger application

# Expose logger for use in submodules
__all__ = ['logger']
