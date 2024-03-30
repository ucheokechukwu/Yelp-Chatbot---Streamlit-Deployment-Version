import os
from typing import Any
import numpy as np
from langchain_community.graphs import Neo4jGraph
import pandas as pd


########geodistance.py####################

# https://nominatim.org/release-docs/develop/api/Search/#geocodejson
# https://project-osrm.org/docs/v5.24.0/api/?language=python#table-service

import requests

headers = {
    'Accept-language': "en-US,en;q=0.9",
    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    'Content-Type':"text"
}

def secs_to_hr_min(duration: float) -> str:
    hrs = int(duration/3600)
    res = duration%3600
    mins = int(res/60)
    secs = int(res%60) if not (mins or hrs) else None
    return (f"{hrs} h " if hrs else " ") + (f"{mins} m " if mins else " ") + (f"{secs} s " if secs else " ")

def get_geolocation(address: str) -> (float, float):
    url = f"https://nominatim.openstreetmap.org/search?q={address}&format=geojson"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data:
            if data['features']:
                lon, lat = data['features'][0]['geometry']['coordinates']
                return lon, lat
    return None

def get_triptime(start_lon_lat, 
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

def main(start_location, end_location):

    # Get geolocation of start and locations
    start_lon_lat = get_geolocation(start_location)
    end_lon_lat = get_geolocation(end_location)

    duration = get_triptime(start_lon_lat, end_lon_lat)
    trip_time = secs_to_hr_min(duration) if duration else None
    return duration, trip_time
    
    
#############################

def _get_current_businesses() -> list[str]:
    """Fetch a list of current business names from a Neo4j database."""
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        )
    current_businesses = graph.query(
        """
        MATCH (b:Business)
        RETURN b.name AS name, 
            b.address as address, 
            b.city as city,
            b.state as state,
            b.postal_code as postal_code 
        """
    )
    return pd.DataFrame(current_businesses)
    
def get_trip_time(business: str or pd.DataFrame, start_location: str) -> (float, str):
    """Get the current trip time to businesses from a given location in seconds."""
    if type(business) == str:
        try:
            current_businesses = _get_current_businesses()
            b = current_businesses[current_businesses.name==business].iloc[0]
        except:
            return -1, f"{business} not found in the database."
    else:
        b = business
    business_location = ' '.join([b['address'], b['city'], b['state'], b['postal_code']])              
    # duration (int), trip_time (str)  
    return main(start_location=start_location,
                            end_location=business_location)                      
                            
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