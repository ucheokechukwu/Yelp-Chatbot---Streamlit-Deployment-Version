from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import PromptTemplate

from backend.tools.trip_times import get_trip_time

import os
import streamlit as st
YELP_QA_MODEL=st.secrets["YELP_QA_MODEL"]


def _invoke_trip_time(inputs):
    print(inputs)
    return get_trip_time(**inputs)

instructions = """You are an expert extraction algorithm. Only extract information from the prompt.
    If you cannot get the value of an attribute asked to extract, return an empty string for the attribute's value.
    
    Instructions:
    1. Parse the given prompt to identify the start location and business name.
    2. The start location is mentioned as the location from which the travel time is measured.
    3. The business name is the destination for which the travel time is requested.
    4. Parse the start location to identify the city and state.
    5. Convert the state name into its 2-letter alpha code. e.g. Texas becomes 'TX', 'Alberta' becomes 'AB', 
    'Ontario' becomes ON. Do not use the full state name.
    6. Return the extracted start location, business name, city and state as 
    "start_location", "business", "city", "state".
    
    # Example:
    - Prompt: 'How long does it take to get from 3342 S West Shore Blvd Tampa, Florida to ABC Store?' 
    - Expected Output:
    "start_location": '3342 S West Shore Blvd Tampa, Florida',
    "business_name": 'ABC Store'
    "city": 'Tampa'
    "state": 'FL'
    
    # Example:
    - Prompt: "Calculate the travel time from 35 Sage Hill Gate NW, Calgary, AB T3R 0S4 to Walmart Superstore."
    - Expected Output:
    "start_location" = '35 Sage Hill Gate NW, Calgary, AB T3R 0S4', 
    "business" = 'Walmart Superstore'
    "city" = 'Calgary'
    "state" = 'AB'
    
    # Example:
    - Prompt: "How quickly can I get to a Target from 431 Round Top St, Webster?"
    - Expected Output:
    "start_location" = '431 Round Top St, Webster', 
    "business" = 'Target'
    "city" = 'Webster'
    "state" = ''
    
    # Example
    - Prompt: "What's the shortest travel time to Homewood Suites from 78481 Ave 42, California, USA?"
    - Expected Output:
    "start_location" = '78481 Ave 42, California', 
    "business" = 'Homewood Suites'
    "city" = ''
    "state" = 'CA'
    
    # Example
    - Prompt: "How quickly can I get to Bob's Bar from 9th Avenue, Ontario?"
    - Expected Output:
    "start_location" = '9th Avenue, Ontario', 
    "business" = "Bob's Bar"
    "city" = ''
    "state" = 'ON'
    
    
    Prompt:
    {prompt}
"""
    
prompt = PromptTemplate(template=instructions,input_variables=["prompt"],)
                    
class Params(BaseModel):
    start_location: str = Field(description="start location")
    business: str = Field(description="business")
    city: str = Field(description="city")
    state: str = Field(description="state")

openai_functions = [convert_to_openai_function(Params)]
model = ChatOpenAI(model=YELP_QA_MODEL, temperature=0)

parser = JsonOutputFunctionsParser()
yelp_triptime_chain = prompt | model.bind(functions=openai_functions) | parser | _invoke_trip_time

def yelp_triptime_chain_invoke(prompt):
    prompt = {"prompt":prompt}
    return yelp_triptime_chain.invoke(prompt)