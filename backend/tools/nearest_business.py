import os
from typing import Any
import numpy as np
from langchain_community.graphs import Neo4jGraph
import pandas as pd
import time
from backend.tools._get_triptime import _get_trip_time_to_business
import inspect

def _get_current_businesses(category: str="", city: str="", state: str="") -> pd.DataFrame:
    print(inspect.currentframe().f_code.co_name)
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
        )
    # construct filter
    category = category.title().replace("'", "\\'")
    q = f"b.state = '{state}'" * bool(state) + " AND " * bool (state and city) + f"toLower(b.city) = '{city.lower()}'" * bool(city)
    query = (f"""MATCH (b:Business) 
            WHERE '{category}' IN b.categories AND {q}
            RETURN b.name AS name, 
                   b.address AS address, 
                   b.city AS city,
                   b.state AS state,
                   b.postal_code AS postal_code""")
       
    current_businesses = graph.query(query)
    return pd.DataFrame(current_businesses)


def get_nearest_business(start_location: str="",
                  business: str="",
                  category: str="",
                  city:str ="",
                  state:str =""):
    """required arguments: start_location, category, at least one of [city, state]"""
    print(inspect.currentframe().f_code.co_name)
    try:
        if not (start_location and category and (city or state)):
            raise ValueError("not enough information for geolocation and routing.")
        current_businesses = _get_current_businesses(category, city, state)
        if current_businesses.empty:
            raise ValueError("returned empty database")
    except Exception as e:
        return -1, f"Error: {e}"
    
    current_businesses["duration"], current_businesses["trip_time"]  = zip(*current_businesses.apply(
                                                                        _get_trip_time_to_business, 
                                                                        axis=1, 
                                                                        start_location=start_location))


    shortest_time_idx = current_businesses["duration"].idxmin()
    nearest_business = current_businesses['name'][shortest_time_idx]
    address = current_businesses['address'][shortest_time_idx]
    shortest_duration = current_businesses['duration'][shortest_time_idx]
    shortest_trip_time = current_businesses['trip_time'][shortest_time_idx]

    return {nearest_business: [address, shortest_duration, shortest_trip_time]}