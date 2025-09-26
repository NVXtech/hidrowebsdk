"""
Configuration settings for HidroWebSDK
"""

import os
from typing import Dict, Any


class Config:
    """Configuration class for HidroWebSDK"""
    
    # API Configuration
    DEFAULT_BASE_URL = "https://www.ana.gov.br/hidrowebservice"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    
    # Known API endpoints
    ENDPOINTS = {
        'stations': '/estacoes',
        'station_detail': '/estacoes/{code}',
        'time_series': '/series',
        'search_stations': '/estacoes/buscar',
    }
    
    # Station types mapping
    STATION_TYPES = {
        'pluviometric': 'pluviométrica',
        'fluviometric': 'fluviométrica', 
        'meteorological': 'meteorológica',
        'water_quality': 'qualidade_agua',
    }
    
    # Data series types
    SERIES_TYPES = {
        'flow': 'vazao',
        'rainfall': 'chuva',
        'water_level': 'cota',
        'temperature': 'temperatura',
        'humidity': 'umidade',
    }
    
    # Brazilian states mapping
    STATES = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas',
        'BA': 'Bahia', 'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo',
        'GO': 'Goiás', 'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul',
        'MG': 'Minas Gerais', 'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná',
        'PE': 'Pernambuco', 'PI': 'Piauí', 'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte',
        'RS': 'Rio Grande do Sul', 'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina',
        'SP': 'São Paulo', 'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL from environment or default"""
        return os.getenv('HIDROWEB_BASE_URL', cls.DEFAULT_BASE_URL)
    
    @classmethod
    def get_timeout(cls) -> int:
        """Get timeout from environment or default"""
        try:
            return int(os.getenv('HIDROWEB_TIMEOUT', cls.DEFAULT_TIMEOUT))
        except ValueError:
            return cls.DEFAULT_TIMEOUT
    
    @classmethod
    def get_max_retries(cls) -> int:
        """Get max retries from environment or default"""
        try:
            return int(os.getenv('HIDROWEB_MAX_RETRIES', cls.DEFAULT_MAX_RETRIES))
        except ValueError:
            return cls.DEFAULT_MAX_RETRIES
    
    @classmethod
    def validate_state(cls, state: str) -> bool:
        """Validate Brazilian state code"""
        return state.upper() in cls.STATES
    
    @classmethod
    def get_station_type_code(cls, station_type: str) -> str:
        """Get API code for station type"""
        return cls.STATION_TYPES.get(station_type.lower(), station_type)
    
    @classmethod
    def get_series_type_code(cls, series_type: str) -> str:
        """Get API code for series type"""
        return cls.SERIES_TYPES.get(series_type.lower(), series_type)