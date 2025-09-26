"""
HidroWebSDK - Python SDK for ANA's HidroWeb API

This package provides a simple interface to communicate with the Brazilian
National Water Agency (ANA) HidroWeb API to access hydrological and
pluviometric data from monitoring stations.

Example:
    >>> from hidrowebsdk import HidroWebClient
    >>> client = HidroWebClient()
    >>> stations = client.get_stations()
"""

from .client import HidroWebClient
from .exceptions import HidroWebError, HidroWebAPIError, HidroWebConnectionError
from .models import Station, TimeSeries

__version__ = "0.1.0"
__author__ = "NVXtech"
__email__ = "contact@nvxtech.com"

__all__ = [
    "HidroWebClient",
    "HidroWebError",
    "HidroWebAPIError", 
    "HidroWebConnectionError",
    "Station",
    "TimeSeries",
]