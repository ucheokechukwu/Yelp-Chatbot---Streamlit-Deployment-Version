# https://nominatim.org/release-docs/develop/api/Search/#geocodejson
# https://project-osrm.org/docs/v5.24.0/api/?language=python#table-service
import time
import requests
import pandas as pd
import inspect

headers = {
    'Accept-language': "en-US,en;q=0.9",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    'Content-Type':"text"
}

def _get_geolocation(address: str) -> (float, float):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=geojson"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            if data['features']:
                lon, lat = data['features'][0]['geometry']['coordinates']
                return lon, lat
    return None

def _get_routetime(start_lon_lat, 
                 end_lon_lat,
                profile = "driving"):
    if start_lon_lat is None or  end_lon_lat is None:
        return None
    # alternative_url_endpoint="https://routing.openstreetmap.de/routed-foot/route/v1/"
    url = f"http://router.project-osrm.org/table/v1/{profile}/{start_lon_lat[0]},{start_lon_lat[-1]};{end_lon_lat[0]},{end_lon_lat[-1]}"
    response = requests.get(url, headers=headers)
    if response.status_code ==200:
        data = response.json()
        if data:
            duration = max(data['durations'][0])
            return duration
    return None
    
def _secs_to_hr_min(duration: float) -> str:
    hrs = int(duration/3600)
    res = duration%3600
    mins = int(res/60)
    secs = int(res%60) if not (mins or hrs) else None
    return (f"{hrs} h " if hrs else " ") + (f"{mins} m " if mins else " ") + (f"{secs} s " if secs else " ")

def _get_triptime(start_location, end_location):
    # Get geolocation of start and locations
    print(inspect.currentframe().f_code.co_name)
    start_lon_lat = _get_geolocation(start_location)
    time.sleep(5)
    end_lon_lat = _get_geolocation(end_location)

    duration = _get_routetime(start_lon_lat, end_lon_lat)
    trip_time = _secs_to_hr_min(duration) if duration else None
    return duration, trip_time
    
    
def _get_trip_time_to_business(b: pd.Series, start_location: str) -> (float, str):
    """Get the current trip time to businesses from a given location in seconds."""
    print(inspect.currentframe().f_code.co_name)
    end_location = ' '.join([b['address'], b['city'], b['state'], b['postal_code']])             
    # duration (int), trip_time (str)  
    return _get_triptime(start_location, end_location) 