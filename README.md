# HidroWebSDK

HidroWebSDK is a Python SDK that simplifies and automates the downloading of hydrological and pluviometric time series data from the Brazilian National Water Agency (ANA) monitoring stations via its official API (HidroWeb).

## Features

- Easy-to-use Python interface for ANA's HidroWeb API
- Access to thousands of hydrological and pluviometric monitoring stations across Brazil
- Retrieve time series data for flow, rainfall, water level, and other measurements
- Built-in data validation and error handling
- Export data to CSV and pandas DataFrames
- Station search and filtering capabilities
- Comprehensive documentation and examples

## Installation

```bash
pip install hidrowebsdk
```

Or install from source:

```bash
git clone https://github.com/NVXtech/hidrowebsdk.git
cd hidrowebsdk
pip install -e .
```

## Quick Start

```python
from hidrowebsdk import HidroWebClient
from datetime import datetime, timedelta

# Initialize the client
client = HidroWebClient()

# Get stations in São Paulo state
stations = client.get_stations(state='SP')
print(f"Found {len(stations)} stations")

# Get detailed information about a station
station = client.get_station_info('12345678')  # Replace with actual station code
print(f"Station: {station.name}")
print(f"Location: {station.latitude}, {station.longitude}")

# Get time series data for the last 30 days
end_date = datetime.now()
start_date = end_date - timedelta(days=30)

time_series = client.get_time_series(
    station_code='12345678',  # Replace with actual station code
    start_date=start_date,
    end_date=end_date,
    series_type='flow'
)

# Convert to pandas DataFrame for analysis
df = time_series.dataframe
print(df.head())

# Search for stations
results = client.search_stations('Rio São Francisco')
for station in results:
    print(f"{station.code}: {station.name}")
```

## API Reference

### HidroWebClient

The main client class for interacting with the ANA HidroWeb API.

#### Methods

- `get_stations(state=None, basin=None, station_type=None)`: Get list of monitoring stations
- `get_station_info(station_code)`: Get detailed information about a specific station  
- `get_time_series(station_code, start_date, end_date, series_type='flow')`: Get time series data
- `search_stations(query, limit=50)`: Search for stations by name or code

### Station

Represents a monitoring station with the following attributes:

- `code`: Station code
- `name`: Station name
- `latitude`, `longitude`: Geographic coordinates
- `state`: State where the station is located
- `municipality`: Municipality name
- `basin`: Hydrographic basin
- `station_type`: Type of station (pluviometric, fluviometric, etc.)

### TimeSeries

Represents time series data with methods:

- `dataframe`: Get data as pandas DataFrame
- Raw data access through `raw_data` attribute

## Configuration

You can configure the SDK using environment variables:

- `HIDROWEB_BASE_URL`: API base URL (default: official ANA URL)
- `HIDROWEB_TIMEOUT`: Request timeout in seconds (default: 30)
- `HIDROWEB_MAX_RETRIES`: Maximum retry attempts (default: 3)

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py`: Basic operations with the SDK
- More examples coming soon...

## Data Types

The SDK supports various types of hydrological data:

- **Flow data** (`flow`): River discharge measurements
- **Rainfall data** (`rainfall`): Precipitation measurements  
- **Water level data** (`water_level`): River/reservoir levels
- **Temperature data** (`temperature`): Water temperature
- **Water quality data** (`water_quality`): Various quality parameters

## Error Handling

The SDK provides specific exception types:

- `HidroWebError`: Base exception class
- `HidroWebAPIError`: API-related errors
- `HidroWebConnectionError`: Network connection errors
- `HidroWebValidationError`: Input validation errors

```python
from hidrowebsdk import HidroWebClient, HidroWebAPIError

try:
    client = HidroWebClient()
    stations = client.get_stations()
except HidroWebAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
except Exception as e:
    print(f"General Error: {e}")
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This is an unofficial SDK for ANA's HidroWeb API. It is not affiliated with or endorsed by ANA (Agência Nacional de Águas e Saneamento Básico).

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/NVXtech/hidrowebsdk/issues) on GitHub.
