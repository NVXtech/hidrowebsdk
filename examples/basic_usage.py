"""
Basic usage example for HidroWebSDK
"""

from hidrowebsdk import HidroWebClient
from datetime import datetime, timedelta


def main():
    # Initialize the client
    client = HidroWebClient()
    
    try:
        # Get stations in São Paulo state
        print("Fetching stations in São Paulo state...")
        stations = client.get_stations(state='SP')
        print(f"Found {len(stations)} stations")
        
        if stations:
            # Show first few stations
            print("\nFirst 5 stations:")
            for station in stations[:5]:
                print(f"  {station.code}: {station.name} ({station.station_type})")
            
            # Get detailed info for first station
            first_station = stations[0]
            print(f"\nDetailed info for station {first_station.code}:")
            detailed_station = client.get_station_info(first_station.code)
            print(f"  Name: {detailed_station.name}")
            print(f"  Location: {detailed_station.latitude}, {detailed_station.longitude}")
            print(f"  Municipality: {detailed_station.municipality}")
            print(f"  Basin: {detailed_station.basin}")
            
            # Get time series data for the last 30 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            
            print(f"\nFetching time series data from {start_date.date()} to {end_date.date()}...")
            time_series = client.get_time_series(
                station_code=first_station.code,
                start_date=start_date,
                end_date=end_date,
                series_type='flow'
            )
            
            print(f"Retrieved {len(time_series)} records")
            if len(time_series) > 0:
                df = time_series.dataframe
                print(f"Data shape: {df.shape}")
                print("\nFirst few records:")
                print(df.head())
        
        # Search for stations
        print("\nSearching for stations with 'Rio' in the name...")
        search_results = client.search_stations('Rio', limit=10)
        print(f"Found {len(search_results)} stations")
        
        for station in search_results[:3]:
            print(f"  {station.code}: {station.name}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close the client
        client.close()


if __name__ == "__main__":
    main()