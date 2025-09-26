"""
Basic tests for HidroWebSDK
"""

import unittest
from unittest.mock import Mock, patch
import pandas as pd

from hidrowebsdk import HidroWebClient, Station, TimeSeries
from hidrowebsdk.exceptions import HidroWebValidationError
from hidrowebsdk.utils import validate_station_code, format_date
from hidrowebsdk.config import Config


class TestHidroWebSDK(unittest.TestCase):
    
    def test_package_imports(self):
        """Test that all main components can be imported"""
        from hidrowebsdk import HidroWebClient, HidroWebError, Station, TimeSeries
        self.assertTrue(True)
    
    def test_client_initialization(self):
        """Test client can be initialized with default parameters"""
        client = HidroWebClient()
        self.assertEqual(client.base_url, Config.DEFAULT_BASE_URL)
        self.assertEqual(client.timeout, Config.DEFAULT_TIMEOUT)
        self.assertEqual(client.max_retries, Config.DEFAULT_MAX_RETRIES)
        client.close()
    
    def test_client_custom_parameters(self):
        """Test client can be initialized with custom parameters"""
        custom_url = "https://custom.api.url"
        custom_timeout = 60
        custom_retries = 5
        
        client = HidroWebClient(
            base_url=custom_url,
            timeout=custom_timeout,
            max_retries=custom_retries
        )
        
        self.assertEqual(client.base_url, custom_url)
        self.assertEqual(client.timeout, custom_timeout)
        self.assertEqual(client.max_retries, custom_retries)
        client.close()
    
    def test_station_model(self):
        """Test Station model creation and methods"""
        station_data = {
            'codigo': '12345678',
            'nome': 'Test Station',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'estado': 'SP',
            'municipio': 'São Paulo',
            'tipo_estacao': 'fluviométrica'
        }
        
        station = Station(station_data)
        self.assertEqual(station.code, '12345678')
        self.assertEqual(station.name, 'Test Station')
        self.assertEqual(station.latitude, -23.5505)
        self.assertEqual(station.longitude, -46.6333)
        self.assertEqual(station.state, 'SP')
        self.assertEqual(station.municipality, 'São Paulo')
        self.assertEqual(station.station_type, 'fluviométrica')
        
        # Test to_dict method
        station_dict = station.to_dict()
        self.assertIsInstance(station_dict, dict)
        self.assertEqual(station_dict['code'], '12345678')
        self.assertEqual(station_dict['name'], 'Test Station')
    
    def test_time_series_model(self):
        """Test TimeSeries model creation"""
        test_data = [
            {'data': '2024-01-01', 'valor': 100.5, 'qualidade': 'Bom'},
            {'data': '2024-01-02', 'valor': 95.2, 'qualidade': 'Bom'},
        ]
        
        time_series = TimeSeries('12345678', test_data, 'flow')
        self.assertEqual(time_series.station_code, '12345678')
        self.assertEqual(time_series.series_type, 'flow')
        self.assertEqual(len(time_series), 2)
        
        # Test dataframe property
        df = time_series.dataframe
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 2)
    
    def test_station_code_validation(self):
        """Test station code validation utility"""
        # Valid codes
        self.assertTrue(validate_station_code('12345678'))
        self.assertTrue(validate_station_code('00001234'))
        
        # Invalid codes
        self.assertFalse(validate_station_code('1234567'))  # Too short
        self.assertFalse(validate_station_code('123456789'))  # Too long
        self.assertFalse(validate_station_code('1234567a'))  # Contains letter
        self.assertFalse(validate_station_code(''))  # Empty
        self.assertFalse(validate_station_code(None))  # None
        self.assertFalse(validate_station_code(12345678))  # Not string
    
    def test_date_formatting(self):
        """Test date formatting utility"""
        from datetime import date, datetime
        
        # Test string dates
        self.assertEqual(format_date('2024-01-01'), '2024-01-01')
        self.assertEqual(format_date('01/01/2024'), '2024-01-01')
        self.assertEqual(format_date('01-01-2024'), '2024-01-01')
        
        # Test date objects
        test_date = date(2024, 1, 1)
        self.assertEqual(format_date(test_date), '2024-01-01')
        
        # Test datetime objects
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        self.assertEqual(format_date(test_datetime), '2024-01-01')
        
        # Test invalid dates
        with self.assertRaises(ValueError):
            format_date('invalid-date')
        
        with self.assertRaises(ValueError):
            format_date(123)
    
    def test_validation_errors(self):
        """Test validation error handling"""
        client = HidroWebClient()
        
        # Test empty station code
        with self.assertRaises(HidroWebValidationError):
            client.get_station_info('')
        
        # Test invalid station code format (should fail validation before network call)
        with self.assertRaises(HidroWebValidationError):
            client.get_station_info('invalid')
        
        # Test invalid station code with time series
        with self.assertRaises(HidroWebValidationError):
            client.get_time_series('invalid', '2024-01-01', '2024-01-02')
        
        client.close()
    
    def test_context_manager(self):
        """Test client as context manager"""
        with HidroWebClient() as client:
            self.assertIsNotNone(client.session)
        
        # Session should be closed after context manager exits
        # Note: This is a basic test, actual session state might vary
    
    def test_config_environment_variables(self):
        """Test configuration with environment variables"""
        import os
        
        # Test default values
        self.assertEqual(Config.get_base_url(), Config.DEFAULT_BASE_URL)
        self.assertEqual(Config.get_timeout(), Config.DEFAULT_TIMEOUT)
        self.assertEqual(Config.get_max_retries(), Config.DEFAULT_MAX_RETRIES)
        
        # Test state validation
        self.assertTrue(Config.validate_state('SP'))
        self.assertTrue(Config.validate_state('sp'))  # Should handle lowercase
        self.assertFalse(Config.validate_state('XX'))


if __name__ == '__main__':
    unittest.main()