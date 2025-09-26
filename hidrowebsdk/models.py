"""
Data models for HidroWebSDK
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd


class Station:
    """Represents a monitoring station from ANA's HidroWeb system"""
    
    def __init__(self, data: Dict[str, Any]):
        self.code: str = data.get('codigo', '')
        self.name: str = data.get('nome', '')
        self.latitude: Optional[float] = data.get('latitude')
        self.longitude: Optional[float] = data.get('longitude')
        self.altitude: Optional[float] = data.get('altitude')
        self.operator: str = data.get('operadora', '')
        self.responsible: str = data.get('responsavel', '')
        self.basin: str = data.get('bacia', '')
        self.sub_basin: str = data.get('sub_bacia', '')
        self.state: str = data.get('estado', '')
        self.municipality: str = data.get('municipio', '')
        self.station_type: str = data.get('tipo_estacao', '')
        self.raw_data = data
    
    def __repr__(self):
        return f"Station(code='{self.code}', name='{self.name}', type='{self.station_type}')"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert station to dictionary"""
        return {
            'code': self.code,
            'name': self.name,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'altitude': self.altitude,
            'operator': self.operator,
            'responsible': self.responsible,
            'basin': self.basin,
            'sub_basin': self.sub_basin,
            'state': self.state,
            'municipality': self.municipality,
            'station_type': self.station_type,
        }


class TimeSeries:
    """Represents time series data from a monitoring station"""
    
    def __init__(self, station_code: str, data: List[Dict[str, Any]], series_type: str = 'flow'):
        self.station_code = station_code
        self.series_type = series_type  # 'flow', 'rainfall', etc.
        self.raw_data = data
        self._df = None
    
    @property
    def dataframe(self) -> pd.DataFrame:
        """Get time series data as pandas DataFrame"""
        if self._df is None:
            self._process_data()
        return self._df
    
    def _process_data(self):
        """Process raw data into pandas DataFrame"""
        if not self.raw_data:
            self._df = pd.DataFrame()
            return
        
        # Convert raw data to DataFrame format
        # The exact structure will depend on the API response format
        processed_data = []
        for record in self.raw_data:
            processed_data.append({
                'date': pd.to_datetime(record.get('data')),
                'value': record.get('valor'),
                'quality': record.get('qualidade', ''),
                'method': record.get('metodo', ''),
            })
        
        self._df = pd.DataFrame(processed_data)
        if not self._df.empty:
            self._df.set_index('date', inplace=True)
            self._df.sort_index(inplace=True)
    
    def __len__(self):
        return len(self.raw_data)
    
    def __repr__(self):
        return f"TimeSeries(station='{self.station_code}', type='{self.series_type}', records={len(self)})"