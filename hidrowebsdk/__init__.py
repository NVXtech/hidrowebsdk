"""
HidroWebSDK - Python SDK for ANA's HidroWeb API

This package provides a simple interface to communicate with the Brazilian
National Water Agency (ANA) HidroWeb API to access hydrological and
pluviometric data from monitoring stations.

Example:
    >>> from hidrowebsdk import Client
    >>> client = Client()
"""

from .client import Client

__version__ = "0.1.0"
__author__ = "NVXtech"
__email__ = "julio.werner@nvxtech.com.br"

__all__ = [
    "Client",
]
