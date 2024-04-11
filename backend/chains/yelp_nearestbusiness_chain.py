from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import PromptTemplate

from backend.tools.nearest_business import get_nearest_business

import os
import streamlit as st
YELP_QA_MODEL=st.secrets["YELP_QA_MODEL"]


def _invoke_nearest_business(inputs):
    print(inputs)
    return get_nearest_business(**inputs)

instructions = """You are an expert extraction algorithm. Only extract information from the prompt.
    If you cannot find the value of an attribute asked to extract, return an empty string for the attribute's value. Do not add any information not stated in the prompt. 
    
    Instructions:
    1. Parse the given prompt to identify the start location and business category.
    2. The start location is mentioned as the location from which the travel time is measured.
    3. The category is part of the description of a possible business destination.
    4. Parse the start location to identify the city and state.
    5. Convert the state name into its 2-letter alpha code. e.g. Texas becomes 'TX', 'Alberta' becomes 'AB', 
    'Ontario' becomes ON. Do not use the full state name.
    6. Return the extracted start location, business category, city and state as 
    "start_location", "business", "city", "state".
    
    # Example:
    - Prompt: 'What's the nearest Hotel to 3342 S West Shore Blvd Tampa, Florida?' 
    - Expected Output:
    "start_location": '3342 S West Shore Blvd Tampa, Florida',
    "category": 'Hotel'
    "city": 'Tampa'
    "state": 'FL'
    
    # Example:
    - Prompt: "What's the closest Supermarket to 35 Sage Hill Gate NW, Calgary, AB T3R 0S4?"
    - Expected Output:
    "start_location" = '35 Sage Hill Gate NW, Calgary, AB T3R 0S4', 
    "category" = 'Supermarket'
    "city" = 'Calgary'
    "state" = 'AB'
    
    # Example:
    - Prompt: "How quickly can I get to a nail salon from 431 Round Top St, Webster?"
    - Expected Output:
    "start_location" = '431 Round Top St, Webster', 
    "category" = 'Nail Salon'
    "city" = 'Webster'
    "state" = ''
    
    # Example
    - Prompt: "From 78481 Ave 42, California, USA, where's the nearest outdoor recreation facility?"
    - Expected Output:
    "start_location" = '78481 Ave 42, California', 
    "category" = 'Outdoor Recreation'
    "city" = ''
    "state" = 'CA'
    
    # Example
    - Prompt: "Is there an Italian Restaurant near 9th Avenue, Ontario?"
    - Expected Output:
    "start_location" = '9th Avenue, Ontario', 
    "category" = "Italian Restaurant"
    "city" = ''
    "state" = 'ON'
    
    
    Prompt:
    {prompt}
"""
    
prompt = PromptTemplate(template=instructions,input_variables=["prompt"],)
                    
class Params(BaseModel):
    start_location: str = Field(description="start location")
    category: str = Field(description="category")
    city: str = Field(description="city")
    state: str = Field(description="state")

openai_functions = [convert_to_openai_function(Params)]
model = ChatOpenAI(model=YELP_QA_MODEL, temperature=0)

parser = JsonOutputFunctionsParser()
yelp_nearestbusiness_chain = prompt | model.bind(functions=openai_functions) | parser | _invoke_nearest_business

def yelp_nearestbusiness_chain_invoke(prompt):
    prompt = {"prompt":prompt}
    return yelp_nearestbusiness_chain.invoke(prompt)