# HidroWebSDK

[![PyPI version](https://badge.fury.io/py/hidrowebsdk.svg)](https://pypi.org/project/hidrowebsdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **⚠️ Warning: This project is under active development and is in alpha stage. APIs may change without notice.**

HidroWebSDK is a Python SDK to simplify and automate the downloading of hydrological data from the Brazilian National Water Agency (ANA) monitoring stations via its official API (HidroWeb).

## Features

- Asynchronous HTTP requests using `httpx` for better performance
- Automatic OAuth token refresh
- Easy-to-use methods for fetching basins, entities, and stations data
- Returns data as Pandas DataFrames for easy analysis
- Comprehensive test suite

## Installation

Install HidroWebSDK using pip:

```bash
pip install hidrowebsdk
```

For development, clone the repository and install with dev dependencies:

```bash
git clone https://github.com/yourusername/hidrowebsdk.git
cd hidrowebsdk
pip install -e ".[dev]"
```

## Usage

### Basic Usage

```python
import asyncio
from hidrowebsdk import Client

async def main():
    # Initialize the client
    client = Client(user="your_user", password="your_password")

    # Authenticate (optional, done automatically on first request)
    await client.authenticate()

    # Fetch all basins
    basins = await client.bacias()
    print(basins.head())

    # Fetch entities with filters
    from datetime import datetime
    entities = await client.entidades(
        last_update_start=datetime(2023, 1, 1),
        last_update_end=datetime(2023, 12, 31)
    )
    print(entities.head())

    # Fetch stations
    stations = await client.estacoes(state="SP")
    print(stations.head())

    # Close the client
    await client.close()

# Run the async function
asyncio.run(main())
```

### Environment Variables

You can set your credentials using environment variables:

```bash
export HIDROWEB_USER="your_user"
export HIDROWEB_PASSWORD="your_password"
```

Then, initialize the client without parameters:

```python
client = Client()
```

## API Reference

### Client

#### `__init__(user=None, password=None)`

Initialize the client with user credentials.

#### `authenticate()`

Authenticate with the HidroWeb API and obtain an access token.

#### `bacias(codigo=None, last_update_start=None, last_update_end=None)`

Fetch basin data.

- `codigo`: Basin code (int)
- `last_update_start`: Start date for last update filter (datetime)
- `last_update_end`: End date for last update filter (datetime)

Returns: Pandas DataFrame

#### `entidades(codigo=None, last_update_start=None, last_update_end=None)`

Fetch entity data.

- `codigo`: Entity code (int)
- `last_update_start`: Start date for last update filter (datetime)
- `last_update_end`: End date for last update filter (datetime)

Returns: Pandas DataFrame

#### `estacoes(codigo=None, last_update_start=None, last_update_end=None, state=None, basin_code=None)`

Fetch station data.

- `codigo`: Station code (int)
- `last_update_start`: Start date for last update filter (datetime)
- `last_update_end`: End date for last update filter (datetime)
- `state`: State abbreviation (str)
- `basin_code`: Basin code (int)

Returns: Pandas DataFrame

#### `close()`

Close the HTTP client connection.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

Run the test suite:

```bash
pytest
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Brazilian National Water Agency (ANA) for providing the HidroWeb API
- Built with [httpx](https://www.python-httpx.org/) for async HTTP requests
- Built with [pandas](https://pandas.pydata.org/) for data manipulation
- Built with [pytest](https://pytest.org/) for testing
