import os
import requests
import streamlit as st
from src.backend import entrypoint

CHATBOT_URL = st.secrets["CHATBOT_URL"]

with st.sidebar:
    st.header("About")
    st.markdown(
        """
                This chatbot interfaces with a
                [LangChain](https://python.langchain.com/docs/get_started/introduction)
                agent to answer questions about (a subset of) users, businesses, 
                and reviews on [Yelp](https://www.yelp.com/). Dataset provided by [Yelp](https://www.yelp.com/dataset).
                The agent uses  retrieval-augment generation (RAG) over both
                structured and unstructured data. Data is hosted by [Neo4js](https://neo4j.com/) Graph Database Management System.
                """
    )
    st.header("Example Questions")
    st.markdown("- Where do people think were the best party venues in 2022?")
    st.markdown("- Which state has the lowest reviewed department stores")
    st.markdown("- Which city has the most recreation facilities?")
    st.markdown("- Where do people find cheap clothes in Texas?")
    st.markdown("- What's the nearest coffee shop to 60 Bridge St, Lowell 01850?")
    
st.title("YelpBot 🤖")
st.info(
    "Ask me questions about businesses, reviews, users and travel times!"
)
if "messages" not in st.session_state:
    st.session_state.messages = []
    
for message in st.session_state.messages:
    with st.chat_message(message['role']):
        if "output" in message.keys():
            st.markdown(message['output'])
        if "explanation" in message.keys():
            with st.status("How was this generated", state="complete"):
                st.info(message["explanation"])
                
if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role":"user", "output":prompt})
    data = {"text": prompt}
    
    with st.spinner("The 🤖 is thinking..."):
        response = requests.post(CHATBOT_URL, json=data)
        if response.status_code == 200:
            output_text = response.json()["output"]
            explanation = response.json()["intermediate_steps"]
        else:
            output_text = """An error occurred while processing your message.
            Please try again or rephrase your message."""
            explantion = output_text
    
    st.chat_message("assistant").markdown(output_text)
    st.status("How was this generated", state="complete").info(explanation)
    
    st.session_state.messages.append(
        {"role": "assistant",
        "output": output_text,
        "explanation": explanation}
    )
    
    
    