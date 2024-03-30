import os
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,)
    
from backend.tools.trip_times import get_trip_time, get_nearest_business
from backend.chains.yelp_review_chain import reviews_vector_chain
from backend.chains.yelp_cypher_chain import yelp_cypher_chain
from backend.chains.yelp_triptime_chain import yelp_triptime_chain_invoke

YELP_AGENT_MODEL = st.secrets["YELP_AGENT_MODEL"]

from langchain import hub
yelp_agent_prompt = hub.pull("hwchase17/openai-functions-agent")


tools = [
    Tool(
        name="Experience",
        func=reviews_vector_chain.invoke,
        description="""Useful when you need to answer questions about user experiences, feelings, preferences, tips, or any other qualitative
        question that could be answered about a business using semantic search. Not useful for answering objective questions that involve 
        counting, percentages, aggregations, or listing facts. Use the entire prompt as input into the tool. For instance, if the prompt is 
        "Do users prefer outdoor to indoor eating?" the input should be "Do users prefer outdoor to indoor eating?"
        """
    ),
    Tool(
        name="Graph",
        func=yelp_cypher_chain.invoke,
        description="""Useful for answering objective or questions that involve counting, percentages, aggregations, or listing facts. 
        Useful for answering questions about users and business details including business categories, locations, business average rating, 
        user review count, time-based information, and quantitative details. 
        Use the entire prompt as input to the tool. For instance, if the prompt is "How many department stores are open in Texas?", 
        the input should be "How many department stores are open in Texas?"
        """
    ),
    Tool(
        name="TripTimes",
        func=yelp_triptime_chain_invoke,
        description="""Useful when asked about travel time from a specified location to a specific business. Prompts might include time-based phrases
        like 'how quickly', 'how fast', 'how soon', 'trip time', etc. 
        The prompt must have at least one full location address. Not useful for answering questions where one location address is not specified.
        This tool can only get the current trip time to the business and does not have any information about aggregate or historical trip times.
        Use the entire prompt as input to the tool. For instance, if the prompt is 
        "What is the trip time between Magnolia Barber Shop and 290 Central St, Lowell, MA 01852", 
        the input should be "What is the trip time between Magnolia Barber Shop and 290 Central St, Lowell, MA 01852"
        """
    ),
    

]
chat_model = ChatOpenAI(model=YELP_AGENT_MODEL, temperature=0)
yelp_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=yelp_agent_prompt,
    tools=tools)
    
yelp_agent_executor = AgentExecutor(
    agent=yelp_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)