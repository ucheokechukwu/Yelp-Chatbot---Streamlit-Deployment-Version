from langchain_core.utils.function_calling import convert_to_openai_function
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain.prompts import PromptTemplate

from src.backend.tools.trip_times import get_trip_time

import os
import streamlit as st
YELP_QA_MODEL=st.secrets["YELP_QA_MODEL"]


def invoke_trip_time(inputs):
    return get_trip_time(**inputs)

instructions = """You are an expert extraction algorithm. Only extract information from the prompt.
    If you cannot get the value of an attribute asked to extract, return null for the attribute's value.
    
    Instructions:
    1. Parse the given prompt to identify the start location and business name.
    2. The start location is mentioned as the location from which the travel time is measured.
    3. The business name is the destination for which the travel time is requested.
    4. Return the extracted start location and business name as "start_location" and "business".
    
    # Example:
    - Prompt: 'How long does it take to get from 456 Pine Avenue to ABC Store?' 
    - Expected Output:
    "start_location": '456 Pine Avenue',
    "business_name": 'ABC Store'
    
    # Example:
    - Prompt: "Calculate the travel time from 123 Main Street, Cityville to ABC Corporation."
    - Expected Output:
    "start_location"="123 Main Street, Cityville", 
    "business"="ABC Corporation"
    
    Prompt:
    {prompt}
"""
    
prompt = PromptTemplate(template=instructions,input_variables=["prompt"],)
                    
class Params(BaseModel):
    start_location: str = Field(description="start location")
    business: str = Field(description="business")

openai_functions = [convert_to_openai_function(Params)]
model = ChatOpenAI(model=YELP_QA_MODEL, temperature=0)

parser = JsonOutputFunctionsParser()
yelp_triptime_chain = prompt | model.bind(functions=openai_functions) | parser | invoke_trip_time

def yelp_triptime_chain_invoke(prompt):
    prompt = {"prompt":prompt}
    return yelp_triptime_chain.invoke(prompt)