"""
Main client class for HidroWebSDK
"""

import requests
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, date
import time
import logging

from .exceptions import HidroWebAPIError, HidroWebConnectionError, HidroWebValidationError
from .models import Station, TimeSeries
from .config import Config
from .utils import validate_station_code, validate_date_range


logger = logging.getLogger(__name__)


class HidroWebClient:
    """
    Client for communicating with ANA's HidroWeb API
    
    The HidroWeb API provides access to hydrological and pluviometric data
    from monitoring stations across Brazil.
    """
    
    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None, max_retries: Optional[int] = None):
        """
        Initialize the HidroWeb client
        
        Args:
            base_url: Base URL for the API (defaults to official ANA URL)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests
        """
        self.base_url = base_url or Config.get_base_url()
        self.timeout = timeout or Config.get_timeout()
        self.max_retries = max_retries or Config.get_max_retries()
        self.session = requests.Session()
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'HidroWebSDK/0.1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None, 
                     method: str = 'GET', data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to the API with retry logic
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            method: HTTP method
            data: Request body data
            
        Returns:
            API response data
            
        Raises:
            HidroWebConnectionError: If connection fails
            HidroWebAPIError: If API returns error response
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=self.timeout
                )
                
                # Check for HTTP errors
                if response.status_code >= 400:
                    error_msg = f"API returned {response.status_code}: {response.reason}"
                    try:
                        error_data = response.json()
                        if 'message' in error_data:
                            error_msg = error_data['message']
                    except ValueError:
                        pass
                    
                    raise HidroWebAPIError(
                        error_msg, 
                        status_code=response.status_code,
                        response_data=response.text
                    )
                
                # Parse JSON response
                try:
                    return response.json()
                except ValueError as e:
                    raise HidroWebAPIError(f"Invalid JSON response: {e}")
                    
            except requests.exceptions.Timeout:
                if attempt < self.max_retries:
                    logger.warning(f"Request timeout, retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                raise HidroWebConnectionError("Request timeout after maximum retries")
                
            except requests.exceptions.ConnectionError as e:
                if attempt < self.max_retries:
                    logger.warning(f"Connection error, retrying in {2 ** attempt} seconds...")
                    time.sleep(2 ** attempt)
                    continue
                raise HidroWebConnectionError(f"Connection error: {e}")
                
            except requests.exceptions.RequestException as e:
                raise HidroWebConnectionError(f"Request failed: {e}")
    
    def get_stations(self, state: Optional[str] = None, basin: Optional[str] = None,
                    station_type: Optional[str] = None) -> List[Station]:
        """
        Get list of monitoring stations
        
        Args:
            state: Filter by state code (e.g., 'SP', 'RJ')
            basin: Filter by basin name
            station_type: Filter by station type ('pluviometric', 'fluviometric', etc.)
            
        Returns:
            List of Station objects
        """
        params = {}
        if state:
            params['estado'] = state
        if basin:
            params['bacia'] = basin
        if station_type:
            params['tipo'] = station_type
        
        try:
            response = self._make_request('/estacoes', params=params)
            
            # The actual response structure will depend on the API
            # This is a generic implementation
            stations_data = response.get('estacoes', [])
            if not isinstance(stations_data, list):
                stations_data = [response]
            
            return [Station(station_data) for station_data in stations_data]
            
        except Exception as e:
            logger.error(f"Failed to get stations: {e}")
            raise
    
    def get_station_info(self, station_code: str) -> Station:
        """
        Get detailed information about a specific station
        
        Args:
            station_code: Station code (e.g., '12345678')
            
        Returns:
            Station object with detailed information
        """
        if not station_code:
            raise HidroWebValidationError("Station code is required")
        
        try:
            response = self._make_request(f'/estacoes/{station_code}')
            return Station(response)
            
        except Exception as e:
            logger.error(f"Failed to get station info for {station_code}: {e}")
            raise
    
    def get_time_series(self, station_code: str, start_date: Union[str, date, datetime],
                       end_date: Union[str, date, datetime], series_type: str = 'flow') -> TimeSeries:
        """
        Get time series data for a station
        
        Args:
            station_code: Station code
            start_date: Start date for data retrieval
            end_date: End date for data retrieval  
            series_type: Type of data ('flow', 'rainfall', etc.)
            
        Returns:
            TimeSeries object with the requested data
        """
        if not station_code:
            raise HidroWebValidationError("Station code is required")
        
        if not validate_station_code(station_code):
            raise HidroWebValidationError(f"Invalid station code format: {station_code}")
        
        # Validate and format dates
        start_date, end_date = validate_date_range(start_date, end_date)
        
        params = {
            'estacao': station_code,
            'dataInicio': start_date,
            'dataFim': end_date,
            'tipo': series_type,
        }
        
        try:
            response = self._make_request('/series', params=params)
            
            # Extract time series data from response
            series_data = response.get('dados', [])
            if not isinstance(series_data, list):
                series_data = []
            
            return TimeSeries(station_code, series_data, series_type)
            
        except Exception as e:
            logger.error(f"Failed to get time series for {station_code}: {e}")
            raise
    
    def search_stations(self, query: str, limit: int = 50) -> List[Station]:
        """
        Search for stations by name or code
        
        Args:
            query: Search query (station name or code)
            limit: Maximum number of results to return
            
        Returns:
            List of matching Station objects
        """
        if not query:
            raise HidroWebValidationError("Search query is required")
        
        params = {
            'busca': query,
            'limite': limit,
        }
        
        try:
            response = self._make_request('/estacoes/buscar', params=params)
            
            stations_data = response.get('estacoes', [])
            if not isinstance(stations_data, list):
                stations_data = []
            
            return [Station(station_data) for station_data in stations_data]
            
        except Exception as e:
            logger.error(f"Failed to search stations with query '{query}': {e}")
            raise
    
    def close(self):
        """Close the HTTP session"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()