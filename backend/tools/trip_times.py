import os
from typing import Any
import numpy as np
from langchain_community.graphs import Neo4jGraph
import pandas as pd
import time


########geodistance.py####################

# https://nominatim.org/release-docs/develop/api/Search/#geocodejson
# https://project-osrm.org/docs/v5.24.0/api/?language=python#table-service

import requests

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
    start_lon_lat = _get_geolocation(start_location)
    time.sleep(5)
    end_lon_lat = _get_geolocation(end_location)

    duration = _get_routetime(start_lon_lat, end_lon_lat)
    trip_time = _secs_to_hr_min(duration) if duration else None
    return duration, trip_time
    
    
#############################

def _get_current_businesses(business_name: str="", city: str="", state: str="") -> pd.DataFrame:
    """Fetch a dataframe of current business names from a Neo4j database."""
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        )
    # construct filter
    business_name = business_name.lower().replace("'", "\\'")
    q = f"b.state = '{state}'" * bool(state) + " AND " * bool (state and city) + f"toLower(b.city) = '{city.lower()}'" * bool(city)
    query = (f"""MATCH (b:Business) 
            WHERE toLower(b.name) CONTAINS '{business_name}' AND {q}
            RETURN b.name AS name, 
                   b.address AS address, 
                   b.city AS city,
                   b.state AS state,
                   b.postal_code AS postal_code 
            LIMIT 5""")

    print(query)               
    current_businesses = graph.query(query)
    return pd.DataFrame(current_businesses)
    
def _get_trip_time_to_business(b: pd.Series, start_location: str) -> (float, str):
    """Get the current trip time to businesses from a given location in seconds."""

    end_location = ' '.join([b['address'], b['city'], b['state'], b['postal_code']])             
    # duration (int), trip_time (str)  
    return _get_triptime(start_location, end_location)                      
                                                     
def get_trip_time(start_location: str="",
                  business: str="",
                  city:str ="",
                  state:str ="") -> "":
    """required arguments: start_location, business_name, at least one of [city, state]"""
    try:
        if not (start_location and business and (city or state)):
            raise ValueError("not enough information for geolocation and routing.")
        current_businesses = _get_current_businesses(business, city, state)
        if current_businesses.empty:
            raise ValueError("returned empty database")
    except Exception as e:
        return -1, f"Error: {e}"
    
    current_businesses["duration"], current_businesses["trip_time"]  = zip(*current_businesses.apply(
                                                                        _get_trip_time_to_business, 
                                                                        axis=1, 
                                                                        start_location=start_location))
    return current_businesses[["duration", "trip_time"]].iloc[0].tolist()                     
                            
def get_nearest_business(start_location: str) -> dict[str, [float, float]]:
    """Find the business with the shortest trip time."""
    current_businesses = _get_current_businesses()
    current_businesses["duration"], current_businesses["trip_time"] = zip(*current_businesses.apply(
                                                                    get_trip_time, axis=1, start_location=start_location))

    shortest_time_idx = current_businesses["duration"].idxmin()
    nearest_business = current_businesses['name'][shortest_time_idx]
    shortest_duration = current_businesses['duration'][shortest_time_idx]
    shortest_trip_time = current_businesses['trip_time'][shortest_time_idx]

    return {nearest_business: [shortest_duration, shortest_trip_time]}