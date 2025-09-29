"""
HidroWebSDK - SDK Python para a API Hidroweb da ANA
===================================================

Este pacote fornece uma interface simples para se comunicar com a API Hidroweb da Agência Nacional de Águas (ANA) e acessar os dados hidrológicos disponíveis.

.. versionadded:: 0.1.0

Exemplo
-------

.. code-block:: python

    >>> from hidrowebsdk import Client
    >>> client = Client()
"""

from .client import Client, RangeFilter, DateFilter

__version__ = "0.1.0"
__author__ = "NVXtech"
__email__ = "julio.werner@nvxtech.com.br"

__all__ = [
    "Client",
    "RangeFilter",
    "DateFilter",
]
