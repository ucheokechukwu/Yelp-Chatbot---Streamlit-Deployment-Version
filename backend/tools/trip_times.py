import os
from typing import Any
import numpy as np
from langchain_community.graphs import Neo4jGraph
import pandas as pd
import time
from backend.tools._get_triptime import _get_trip_time_to_business



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
            LIMIT 1""")
       
    current_businesses = graph.query(query)
    return pd.DataFrame(current_businesses)
                   
                                                     
def get_trip_time(start_location: str="",
                  business: str="",
                  city:str ="",
                  state:str =""):
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
    # return current_businesses[["duration", "trip_time"]].iloc[0].tolist()  
    return current_businesses[["duration", "trip_time"]]   
    
    
