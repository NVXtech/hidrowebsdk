"""
Utility functions for HidroWebSDK
"""

import re
from typing import Union, Optional, List, Dict, Any
from datetime import datetime, date
import pandas as pd


def validate_station_code(code: str) -> bool:
    """
    Validate ANA station code format
    
    Args:
        code: Station code to validate
        
    Returns:
        True if valid format, False otherwise
    """
    if not isinstance(code, str):
        return False
    
    # ANA station codes are typically 8 digits
    return bool(re.match(r'^\d{8}$', code.strip()))


def format_date(date_input: Union[str, date, datetime]) -> str:
    """
    Format date for API requests
    
    Args:
        date_input: Date in various formats
        
    Returns:
        Date string in YYYY-MM-DD format
        
    Raises:
        ValueError: If date format is invalid
    """
    if isinstance(date_input, datetime):
        return date_input.strftime('%Y-%m-%d')
    elif isinstance(date_input, date):
        return date_input.strftime('%Y-%m-%d')
    elif isinstance(date_input, str):
        # Try to parse common date formats
        for fmt in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%Y/%m/%d']:
            try:
                parsed_date = datetime.strptime(date_input.strip(), fmt)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue
        raise ValueError(f"Unable to parse date: {date_input}")
    else:
        raise ValueError(f"Invalid date type: {type(date_input)}")


def validate_date_range(start_date: Union[str, date, datetime], 
                       end_date: Union[str, date, datetime]) -> tuple:
    """
    Validate and format date range
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        Tuple of formatted start and end dates
        
    Raises:
        ValueError: If dates are invalid or end_date < start_date
    """
    formatted_start = format_date(start_date)
    formatted_end = format_date(end_date)
    
    start_dt = datetime.strptime(formatted_start, '%Y-%m-%d')
    end_dt = datetime.strptime(formatted_end, '%Y-%m-%d')
    
    if end_dt < start_dt:
        raise ValueError("End date must be after start date")
    
    return formatted_start, formatted_end


def clean_data_value(value: Any) -> Optional[float]:
    """
    Clean and convert data values to float
    
    Args:
        value: Raw data value
        
    Returns:
        Cleaned float value or None if invalid
    """
    if value is None or value == '':
        return None
    
    if isinstance(value, (int, float)):
        return float(value)
    
    if isinstance(value, str):
        # Remove common non-numeric characters
        cleaned = value.strip().replace(',', '.')
        
        # Handle special values
        if cleaned.lower() in ['null', 'nan', 'n/a', '-', '--']:
            return None
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    return None


def filter_stations_by_distance(stations: List[Dict[str, Any]], 
                               center_lat: float, center_lon: float,
                               max_distance_km: float) -> List[Dict[str, Any]]:
    """
    Filter stations by distance from a center point
    
    Args:
        stations: List of station dictionaries
        center_lat: Center latitude
        center_lon: Center longitude
        max_distance_km: Maximum distance in kilometers
        
    Returns:
        Filtered list of stations within the specified distance
    """
    import math
    
    def haversine_distance(lat1, lon1, lat2, lon2):
        """Calculate haversine distance between two points"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = (math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2)
        c = 2 * math.asin(math.sqrt(a))
        
        return R * c
    
    filtered_stations = []
    for station in stations:
        station_lat = station.get('latitude')
        station_lon = station.get('longitude')
        
        if station_lat is not None and station_lon is not None:
            distance = haversine_distance(center_lat, center_lon, station_lat, station_lon)
            if distance <= max_distance_km:
                station['distance_km'] = round(distance, 2)
                filtered_stations.append(station)
    
    # Sort by distance
    return sorted(filtered_stations, key=lambda x: x.get('distance_km', float('inf')))


def export_to_csv(data: Union[pd.DataFrame, List[Dict]], filename: str) -> str:
    """
    Export data to CSV file
    
    Args:
        data: Data to export (DataFrame or list of dictionaries)
        filename: Output filename
        
    Returns:
        Path to created file
    """
    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = data
    
    df.to_csv(filename, index=False)
    return filename


def create_station_summary(stations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create summary statistics for a list of stations
    
    Args:
        stations: List of station dictionaries
        
    Returns:
        Dictionary with summary statistics
    """
    if not stations:
        return {'total': 0}
    
    summary = {
        'total': len(stations),
        'by_state': {},
        'by_type': {},
        'by_operator': {}
    }
    
    for station in stations:
        # Count by state
        state = station.get('state', 'Unknown')
        summary['by_state'][state] = summary['by_state'].get(state, 0) + 1
        
        # Count by type
        station_type = station.get('station_type', 'Unknown')
        summary['by_type'][station_type] = summary['by_type'].get(station_type, 0) + 1
        
        # Count by operator
        operator = station.get('operator', 'Unknown')
        summary['by_operator'][operator] = summary['by_operator'].get(operator, 0) + 1
    
    return summary